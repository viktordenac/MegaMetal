from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import func, select

#python -m pip install flask_sqlalchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Replace the following with your actual PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:potgresql@192.168.100.216/megametal'

# Initialize SQLAlchemy extension
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Example user model
class User(UserMixin):
    def __init__(self, Kartica, Username, Mjesto):
        self.id = Kartica
        self.username = Username
        self.role = Mjesto

    def is_authenticated(self):
        return True  # Assuming all users are authenticated

    def is_active(self):
        return True  # Assuming all users are active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class TBA_RAD(db.Model):
    __tablename__ = 'TBA_RAD'
    Ime = db.Column(db.String(100))
    Kartica = db.Column(db.Numeric(25, 0), primary_key=True)
    Mjesto = db.Column(db.CHAR(15))
    Username = db.Column(db.CHAR(15))
    Password = db.Column(db.CHAR(10))
    Datexp = db.Column(db.DateTime())

class TREZ_TIME(db.Model):
    __tablename__ = 'TREZ_TIME'
    JobCode = db.Column(db.CHAR(25), primary_key=True)
    DateCreated = db.Column(db.DateTime)
    Postotak = db.Column(db.REAL)

class TREZ_KALK(db.Model):
    __tablename__ = 'TREZ_KALK'
    Ident = db.Column(db.CHAR(10), primary_key=True)
    Id_rn = db.Column(db.Integer, primary_key=True)  # Define additional columns as per your table schema
    Bruto = db.Column(db.REAL)
    Debljina = db.Column(db.INT())
    Kvaliteta = db.Column(db.CHAR(20))  # Adjust data type and length as per your table schema

class TEV_EVID(db.Model):
    __tablename__ = 'TEV_EVID'
    ID = db.Column(db.INT(), primary_key=True)
    Datum = db.Column(db.DATE())
    Izmena = db.Column(db.INT())
    Faza = db.Column(db.CHAR(50))
    Opombe = db.Column(db.CHAR(100))
    Vrijeme = db.Column(db.FLOAT())
    Kartica = db.Column(db.Numeric(25, 0))
    Id_rn = db.Column(db.CHAR(50))


@login_manager.user_loader
def load_user(kartica):
    employee = TBA_RAD.query.filter_by(Kartica=kartica).first()
    if employee:
        return User(employee.Kartica, employee.Username, employee.Mjesto)
    return None

def is_authenticated():
    return "username" in session

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form_username = request.form["username"]
        form_password = request.form["password"]
        user = TBA_RAD.query.filter_by(Username=form_username).first()

        if form_username in ['uprava', 'proizvodnja', 'prodaja']:
            if user.Datexp < date.today():
                print(user.Datexp)
                return render_template("login.html", error="Invalid username or password.")

        if user and form_password == str(user.Password):
            # Authentication successful
            login_user(User(user.Kartica, user.Username, user.Mjesto))
            session["username"] = user.Username
            session["role"] = user.Mjesto
            return redirect(url_for('index'))
        else:
            # Authentication failed
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html", error=None)


@app.route("/upravaHome")
def uprava_home():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    username = session["username"]
    return render_template("/Uprava/upravaHome.html", Username=username)

@app.route("/proizvodnjaHome")
def proizvodnja():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Proizvodnja':
        return render_template('unauthorized.html')
    username = session["username"]
    return render_template("/Proizvodnja/proizvodnjaHome.html", Username=username)

@app.route("/prodajaHome")
def prodaja():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Prodaja':
        return render_template('unauthorized.html')
    username = session["username"]
    return render_template("/Prodaja/prodajaHome.html", Username=username)

@app.route("/Potrosnja_materiala")
def potrosnja_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    return render_template("/Uprava/potrosnja_materiala_grafi.html")

@app.route("/Grupiranje_materiala")
def grupiranje_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava' and current_user.role != 'Prodaja':
        return render_template('unauthorized.html')
    if current_user.role == 'Prodaja':
        return render_template("/Prodaja/grupiranje_materiala_proizvodnja.html")
    else:
        return render_template("/Uprava/grupiranje_materiala.html")

@app.route("/Potrošnja-materiala-grafi")
def potrosnja_materiala_grafi():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"})

    # Retrieve 'from_date' and 'to_date' from request parameters
    from_date_str = request.args.get('from_date', '2024-01-01')
    to_date_str = request.args.get('to_date', '2024-12-31')

    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    # Query the database for records within the specified date range
    result = TREZ_TIME.query.filter(TREZ_TIME.DateCreated.between(from_date, to_date)).all()

    if result:
        data = []
        #print("Rows found for date range:", from_date_str, "to", to_date_str)
        # Formatting the results
        for row in result:
            try:
                row.Postotak = int(row.Postotak * 100)
            except:
                row.Postotak = 0
            data.append({
                "JobCode": row.JobCode,
                "DateCreated": row.DateCreated.strftime('%Y-%m-%d'),
                "Postotak": row.Postotak
            })
            #print(row.JobCode, row.DateCreated, row.Postotak)
        return jsonify({"data": data})
    else:
        #print("No rows found for date range:", from_date_str, "to", to_date_str)
        return jsonify({"error": "No data found"})


from collections import defaultdict


@app.route("/Grupiranje_materiala_table", methods=['POST'])
def grupiranje_materiala_table():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"})

    documentId = request.form.get('documentInput')

    try:
        # Fetch data from the database and create a pandas DataFrame
        allData = TREZ_KALK.query.with_entities(TREZ_KALK.Id_rn, func.sum(TREZ_KALK.Bruto)).group_by(TREZ_KALK.Id_rn).all()
        filtered_results = [row for row in allData if row[0] == documentId]
        filtered_bruto = [row[1] for row in filtered_results]

        if not filtered_results:
            return jsonify({"error": "No data found for the given document ID"})

        # Return only display_ident and display_bruto
        return jsonify({'Id_rn': documentId, 'Bruto': filtered_bruto})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    if current_user.role == 'Uprava':
        # Return page accessible to 'uprava' role
        return redirect(url_for("uprava_home"))
    elif current_user.role == 'Proizvodnja':
        # Return page accessible to 'prodaja' role
        return redirect(url_for("proizvodnja"))
    elif current_user.role == 'Prodaja':
        # Return page accessible to 'prodaja' role
        return redirect(url_for("prodaja"))
    else:
        # Handle other roles or unauthorized access
        return render_template('unauthorized.html')


@app.route('/user')
def user():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    # Query all data
    data = TBA_RAD.query.all()

    unique_values = {}
    for column in TBA_RAD.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    return render_template('/Uprava/add_user.html', data=data, unique_values=unique_values)

@app.route('/add_user', methods=['POST'])
def add_user():
    # Get data from the form submission
    name = request.form.get('name')
    username = request.form.get('username')
    kartica = request.form.get('kartica')
    mjesto = request.form.get('mjesto')
    password = request.form.get('password')
    if(request.form.get('datexp') != ''):
        datexp = request.form.get('datexp')
    else:
        datexp = None

    # Check if a user with the same username already exists
    existing_user = TBA_RAD.query.filter_by(Username=username).first()
    if existing_user:
        # User already exists, prompt the user for confirmation
        return jsonify({'prompt': True, 'username': username})

    # User does not exist, proceed with adding the user
    new_user = TBA_RAD(Ime=name, Kartica=kartica, Mjesto=mjesto, Username=username, Password=password, Datexp=datexp)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/edit_user', methods=['POST'])
def edit_user():
    # Get data from the form submission
    username = request.form.get('username')
    # Retrieve other form data as needed

    user = TBA_RAD.query.filter_by(Username=username).first()
    user.Ime = request.form.get('name')
    user.Kartica = request.form.get('kartica')
    user.Mjesto = request.form.get('mjesto')
    user.Password = request.form.get('password')
    if(request.form.get('datexp') != ''):
        user.Datexp = request.form.get('datexp')
    else:
        user.Datexp = None
    db.session.commit()

    # Return a JSON response indicating success
    return jsonify({'success': True})

from flask import request, jsonify

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        # Get the username to delete from the request
        username = request.json.get('username')

        # Check if the user exists
        user = TBA_RAD.query.filter_by(Username=username).first()
        if user:
            try:
                # Delete the user from the database
                db.session.delete(user)
                db.session.commit()
                return jsonify({'success': True})
            except Exception as e:
                # Handle any errors that occur during deletion
                print(e)
                return jsonify({'success': False, 'error': 'Failed to delete user.'}), 500
        else:
            # Return a message indicating that the user does not exist
            return jsonify({'success': False, 'error': 'User not found.'}), 404


@app.route('/tev_evid')
def tev_evid():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')

    # Query all data
    data = TEV_EVID.query.all()

    unique_values = {}
    for column in TEV_EVID.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if
                                      getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
        print("AAAA" + str(unique_values[column_name]))

    return render_template('/Uprava/evidencaUr.html', data=data, unique_values=unique_values)

from flask import request

@app.route('/edit_tev_evid', methods=['POST'])
def edit_tev_evid():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')

    # Get data from the form
    ID = request.form.get('ID')
    datum = request.form.get('datum')
    izmena = request.form.get('izmena')
    faza = request.form.get('faza')
    opombe = request.form.get('opombe')
    vrijeme = request.form.get('vrijeme')
    kartica = request.form.get('kartica')
    id_rn = request.form.get('id_rn')

    # Find the TEV EVID record to edit
    tev_evid_record = TEV_EVID.query.filter_by(ID=ID).first()
    print(tev_evid_record)
    # Update the record with the new data
    if tev_evid_record:
        tev_evid_record.Datum = datum
        tev_evid_record.Izmena = izmena
        tev_evid_record.Faza = faza
        tev_evid_record.Opombe = opombe
        tev_evid_record.Vrijeme = vrijeme
        tev_evid_record.Id_rn = id_rn
        db.session.commit()

        # Optionally, you can return a success response
        return jsonify({'success': True})
    else:
        # Return an error response if the record was not found
        return jsonify({'success': False, 'message': 'TEV EVID record not found'})

@app.route('/delete_tev_evid', methods=['POST'])
def delete_tev_evid():
    if request.method == 'POST':
        # Get the id_rn of the TEV EVID entry to delete from the request
        id_rn = request.json.get('id_rn')

        # Check if the TEV EVID entry exists
        tev_evid_entry = TEV_EVID.query.filter_by(Id_rn=id_rn).first()
        if tev_evid_entry:
            try:
                # Delete the TEV EVID entry from the database
                db.session.delete(tev_evid_entry)
                db.session.commit()
                return jsonify({'success': True})
            except Exception as e:
                # Handle any errors that occur during deletion
                print(e)
                return jsonify({'success': False, 'error': 'Failed to delete TEV EVID entry.'}), 500
        else:
            # Return a message indicating that the TEV EVID entry does not exist
            return jsonify({'success': False, 'error': 'TEV EVID entry not found.'}), 404

if __name__ == "__main__":
    app.run(debug=True)
