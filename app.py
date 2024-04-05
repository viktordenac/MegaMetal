from datetime import datetime, date


import pandas as pd

from flask import Flask, render_template, redirect, url_for, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from io import BytesIO
import openpyxl

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
    def __init__(self, Kartica, Username, Ime, Mjesto):
        self.id = Kartica
        self.username = Username
        self.name = Ime
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

class TEV_IZMENE(db.Model):
    __tablename__ = 'TEV_IZMENE'
    ID = db.Column(db.INT(), primary_key=True)
    Oddelek = db.Column(db.CHAR(50))
    Izmjena = db.Column(db.INT())

class TRN_RN(db.Model):
    __tablename__ = 'TRN_RN'
    Id_rn = db.Column(db.CHAR(50), primary_key=True)
    Status = db.Column(db.CHAR(15))
    Aktivan = db.Column(db.CHAR(2))

@login_manager.user_loader
def load_user(kartica):
    employee = TBA_RAD.query.filter_by(Kartica=kartica).first()
    if employee:
        return User(employee.Kartica, employee.Username, employee.Ime, employee.Mjesto)
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
                return render_template("login.html", error="Invalid username or password.")

        if user and form_password == str(user.Password):
            # Authentication successful
            login_user(User(user.Kartica, user.Username, user.Ime, user.Mjesto))
            session["username"] = user.Username
            session["role"] = user.Mjesto
            session["name"] = user.Ime
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
    name = session["name"]
    return render_template("/Uprava/upravaHome.html", Username=username, Ime=name)

@app.route("/proizvodnjaMM1PosHome")
def proizvodnjaMM1Pos():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'MM1Pos':
        return render_template('unauthorized.html')
    username = session["username"]
    name = session["name"]
    return render_template("/Proizvodnja/MM1Pos/proizvodnjaHome.html", Username=username, Ime=name)

@app.route("/prodajaHome")
def prodaja():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Prodaja':
        return render_template('unauthorized.html')
    username = session["username"]
    name = session["name"]
    return render_template("/Prodaja/prodajaHome.html", Username=username, Ime=name)

@app.route("/konPosHome")
def konPos():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'KonPos':
        return render_template('unauthorized.html')
    username = session["username"]
    name = session["name"]
    return render_template("/Konstrukcija/Poslovodja/konPoslovodjaHome.html", Username=username, Ime=name)

@app.route("/rezPosHome")
def rezPos():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'RezPos':
        return render_template('unauthorized.html')
    username = session["username"]
    name = session["name"]
    return render_template("/Rezanje/Poslovodja/rezPoslovodjaHome.html", Username=username, Ime=name)

@app.route("/Potrosnja_materiala")
def potrosnja_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava' and current_user.role != 'KonPos' and current_user.role != 'RezPos':
        return render_template('unauthorized.html')
    elif current_user.role == 'KonPos':
        return render_template("/Konstrukcija/Poslovodja/potrosnja_materiala_grafi_konstrukcija.html")
    elif current_user.role == 'RezPos':
        return render_template("/Rezanje/Poslovodja/potrosnja_materiala_grafi_rezanje.html")
    return render_template("/Uprava/potrosnja_materiala_grafi.html")

@app.route("/Potrosnja_materiala_torta")
def potrosnja_materiala_torta():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava' and current_user.role != 'KonPos' and current_user.role != 'RezPos':
        return render_template('unauthorized.html')
    elif current_user.role == 'KonPos':
        return render_template("/Konstrukcija/Poslovodja/potrosnja_materiala_torta_konstrukcija.html")
    elif current_user.role == 'RezPos':
        return render_template("/Rezanje/Poslovodja/potrosnja_materiala_torta_rezanje.html")
    return render_template("/Uprava/potrosnja_materiala_torta.html")

@app.route("/Grupiranje_materiala")
def grupiranje_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    identi = TREZ_KALK.query.with_entities(TREZ_KALK.Ident).distinct().all()
    identi = [row[0] for row in identi]

    if current_user.role != 'Uprava' and current_user.role != 'Prodaja' and current_user.role != 'KonPos' and current_user.role != 'RezPos':
        return render_template('unauthorized.html')
    elif current_user.role == 'Prodaja':
        return render_template("/Prodaja/grupiranje_materiala_prodaja.html", radniNalogi=identi)
    elif current_user.role == 'KonPos':
        return render_template("/Konstrukcija/Poslovodja/grupiranje_materiala_konstrukcija.html", radniNalogi=identi)
    elif current_user.role == 'RezPos':
        return render_template("/Rezanje/Poslovodja/grupiranje_materiala_rezanje.html", radniNalogi=identi)
    elif current_user.role == 'MM1Pos':
        return render_template("/Proizvodnja/MM1Pos/grupiranje_materiala_proizvodnja.html", radniNalogi=identi)
    else:
        return render_template("/Uprava/grupiranje_materiala.html", radniNalogi=identi)

@app.route("/Aktivni_nalogi")
def aktivni_nalogi():
    if not is_authenticated():
        return redirect(url_for("login"))

    # Get the status parameter from the request
    status = request.args.get('status', default='1')  # Default value is '1' if parameter is not provided

    # Query data based on the status
    data = TRN_RN.query.filter(TRN_RN.Aktivan == status).all()

    unique_values = {}
    for column in TRN_RN.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if
                                      getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    if current_user.role != 'Uprava' and current_user.role != 'MM1Pos':
        return render_template('unauthorized.html')
    elif current_user.role == 'MM1Pos':
        return render_template("/Proizvodnja/MM1Pos/aktivniNalogi.html", data=data, unique_values=unique_values)
    return render_template("/Uprava/aktivniNalogi.html", data=data, unique_values=unique_values)

@app.route("/Edit-Aktivni-Nalogi", methods=['POST'])
def edit_aktivni_nalogi():
    if not is_authenticated():
        return redirect(url_for("login"))
    # Get data from the form submission
    id_rn = request.form.get('id_rn')
    # Retrieve other form data as needed
    nalog = TRN_RN.query.filter_by(Id_rn=id_rn).first()
    nalog.Status = request.form.get('status')
    nalog.Aktivan = request.form.get('aktivan')
    db.session.commit()

    # Return a JSON response indicating success
    return jsonify({'success': True})

@app.route('/delete_nalog', methods=['POST'])
def delete_nalog():
    if request.method == 'POST':
        # Get the username to delete from the request
        nalog = request.json.get('nalog')

        # Check if the user exists
        nalog = TRN_RN.query.filter_by(Id_rn=nalog).first()
        if nalog:
            try:
                # Delete the user from the database
                db.session.delete(nalog)
                db.session.commit()
                return jsonify({'success': True})
            except Exception as e:
                # Handle any errors that occur during deletion
                return jsonify({'success': False, 'error': 'Failed to delete user.'}), 500
        else:
            # Return a message indicating that the user does not exist
            return jsonify({'success': False, 'error': 'User not found.'}), 404

@app.route('/Add-Aktivni-Nalog', methods=['POST'])
def add_aktivni_nalog():
    # Get data from the form submission
    id_rn = request.form.get('id_rn')
    aktivan = request.form.get('aktivan')

    # Check if a user with the same username already exists
    existing_user = TRN_RN.query.filter_by(Id_rn=id_rn).first()
    if existing_user:
        # User already exists, prompt the user for confirmation
        return jsonify({'prompt': True, 'username': id_rn})

    # User does not exist, proceed with adding the user
    new_nalog = TRN_RN(Id_rn=id_rn, Aktivan=aktivan)
    db.session.add(new_nalog)
    db.session.commit()

    return jsonify({'success': True})

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

@app.route("/Grupiranje_materiala_table", methods=['POST'])
def grupiranje_materiala_table():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"})

    documentId = request.form.get('documentInput')

    try:
        # Fetch data from the database
        sumData = TREZ_KALK.query.with_entities(TREZ_KALK.Ident, func.sum(TREZ_KALK.Bruto)).group_by(TREZ_KALK.Ident).all()
        filtered_results = [(row[0], float(row[1])) for row in sumData if row[0] == documentId]
        filtered_bruto = [row[1] for row in filtered_results]

        allData = TREZ_KALK.query.with_entities(TREZ_KALK.Ident, TREZ_KALK.Id_rn, func.sum(TREZ_KALK.Bruto)).filter_by(
            Ident=documentId).group_by(TREZ_KALK.Ident, TREZ_KALK.Id_rn).all()


        if not filtered_results and not allData:
            return jsonify({"error": "No data found for the given document ID"})

        # Convert allData to a list of dictionaries
        all_data_dict = [{'Ident': row[0], 'Id_rn': row[1], 'Bruto': row[2]} for row in allData]

        # Return JSON response
        return jsonify({'AllData': all_data_dict, 'skupnoBruto': filtered_bruto})

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
    elif current_user.role == 'MM1Pos':
        # Return page accessible to 'prodaja' role
        return redirect(url_for("proizvodnjaMM1Pos"))
    elif current_user.role == 'Prodaja':
        # Return page accessible to 'prodaja' role
        return redirect(url_for("prodaja"))
    elif current_user.role == 'KonPos':
        # Return page accessible to 'konPos' role
        return redirect(url_for("konPos"))
    elif current_user.role == 'RezPos':
        # Return page accessible to 'rezPos' role
        return redirect(url_for("rezPos"))
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
                return jsonify({'success': False, 'error': 'Failed to delete user.'}), 500
        else:
            # Return a message indicating that the user does not exist
            return jsonify({'success': False, 'error': 'User not found.'}), 404


@app.route('/tev_evid')
def tev_evid():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava' and current_user.role != 'MM1Pos':
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
    if current_user.role == 'MM1Pos':
        return render_template('/Proizvodnja/MM1Pos/evidencaUr.html', data=data, unique_values=unique_values)
    return render_template('/Uprava/evidencaUr.html', data=data, unique_values=unique_values)

from flask import request

@app.route('/edit_tev_evid', methods=['POST'])
def edit_tev_evid():
    if not is_authenticated():
        return redirect(url_for("login"))

    if current_user.role != 'Uprava' and current_user.role != 'MM1Pos':
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
                return jsonify({'success': False, 'error': 'Failed to delete TEV EVID entry.'}), 500
        else:
            # Return a message indicating that the TEV EVID entry does not exist
            return jsonify({'success': False, 'error': 'TEV EVID entry not found.'}), 404

@app.route('/planiranjePripravnegaDela')
def planiranjePripravnegaDela():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'MM1Pos' and current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    if current_user.role == 'MM1Pos':
        return render_template("/Proizvodnja/MM1Pos/planiranjePripravnegaDela.html")
    return render_template('/Uprava/planiranjePripravnegaDela.html')


@app.route('/evidencaUr/download', methods=['GET'])
def download_evidencaUr():
    # Query data from the database
    tev_evid_data = TEV_EVID.query.all()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame([(item.ID, item.Datum, item.Izmena, item.Faza, item.Opombe, item.Vrijeme, item.Kartica, item.Id_rn) for item in tev_evid_data], columns=['ID', 'Datum', 'Izmena', 'Faza', 'Opombe', 'Vrijeme', 'Kartica', 'Id_rn'])

    # Convert 'Datum' column to datetime if not already
    df['Datum'] = pd.to_datetime(df['Datum'])

    # Format 'Datum' column as short date
    df['Datum'] = df['Datum'].dt.strftime('%d/%m/%Y')

    # Create an output stream
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Write the DataFrame to Excel
    df.to_excel(writer, index=False, sheet_name='TEV_EVID')

    # Close the Pandas Excel writer
    writer.close()

    # Go back to the beginning of the stream
    output.seek(0)

    # Return the Excel file as a downloadable attachment
    return send_file(output, download_name="TEV_EVID.xlsx", as_attachment=True)

@app.route('/kapaciteta', methods=['GET'])
def kapaciteta():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    return render_template('/Uprava/kapaciteta.html')

@app.route('/izmene', methods=['GET'])
def izmene():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    return render_template('/Uprava/izmene.html')

@app.route('/editIzmene', methods=['POST'])
def edit_izmene():
    if not is_authenticated():
        return redirect(url_for("login"))

    if current_user.role != 'Uprava' and current_user.role != 'MM1Pos':
        return render_template('unauthorized.html')

    # Get data from the form
    id = request.form.get('ID')
    oddelek = request.form.get('Oddelek')
    izmjena = request.form.get('Izmjena')

    # Find the TEV EVID record to edit
    tev_evid_record = TEV_EVID.query.filter_by(ID=id).first()
    # Update the record with the new data
    if tev_evid_record:
        tev_evid_record.Oddelek = oddelek
        tev_evid_record.Izmjena = izmjena
        db.session.commit()

        # Optionally, you can return a success response
        return jsonify({'success': True})
    else:
        # Return an error response if the record was not found
        return jsonify({'success': False, 'message': 'TEV EVID record not found'})

@app.route('/izmene/download', methods=['GET'])
def download_izmene():
    # Query data from the database
    tev_evid_data = TEV_EVID.query.all()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame([(item.ID, item.Oddelek, item.Izmjena) for item in tev_evid_data], columns=['ID', 'Oddelek', 'Izmjena'])

    # Create an output stream
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Write the DataFrame to Excel
    df.to_excel(writer, index=False, sheet_name='TEV_EVID')

    # Close the Pandas Excel writer
    writer.close()

    # Go back to the beginning of the stream
    output.seek(0)

    # Return the Excel file as a downloadable attachment
    return send_file(output, download_name="TEV_EVID.xlsx", as_attachment=True)

@app.route('/verzugsLista', methods=['GET'])
def verzugsLista():
    if not is_authenticated():
        return redirect(url_for("login"))
    if current_user.role != 'Uprava':
        return render_template('unauthorized.html')
    return render_template('/General/vercugsLista.html')

@app.route('/verzugsListaLoad', methods=['GET'])
def verzugsListaLoad():
    if not is_authenticated():
        return redirect(url_for("login"))
    today = datetime.now()

    godina = today.strftime('%Y')
    mjesec = today.strftime('%m')
    dan = today.strftime('%d')
    file_path = "//192.168.100.216/Users/ivan.tonkic/Desktop/Share/Verzugs_liste/Verzugs_lista_"+ dan + "-" + mjesec + "-" + godina + ".xlsx"
    try:
        dfs = pd.read_excel(file_path, sheet_name=None, header=None)
        sheet_names = list(dfs.keys())
        data = {sheet_name: replace_nan(df.values.tolist()) for sheet_name, df in dfs.items()}
        return jsonify({'sheet_names': sheet_names, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)})

def replace_nan(data):
    return [[cell if not pd.isna(cell) else None for cell in row] for row in data]

if __name__ == "__main__":
    #app.run(host='192.168.100.216', port=5000)
    app.run(debug=True)
