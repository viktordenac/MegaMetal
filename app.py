from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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

# @app.route("/add_user", methods=["GET", "POST"])
# def add_user():
#TODO FIX ADD USER
#     if not is_authenticated():
#         return redirect(url_for("login"))
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         role = request.form["role"]
#         if .get(session["username"], {}).get("role") == "admin":
#             users[username] = {"password": password, "role": role}
#             return redirect(url_for("home"))
#         else:
#             return "Unauthorized: Only admin users can add new users."
#     return render_template("add_user.html")


@app.route("/Potrosnja_materiala")
def potrosnja_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template("/Uprava/potrosnja_materiala_grafi.html")

@app.route("/Grupiranje_materiala")
def grupiranje_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template("/Uprava/grupiranje_materiala.html")

@app.route("/Potrošnja materiala grafi")
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
        print("Rows found for date range:", from_date_str, "to", to_date_str)
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
            print(row.JobCode, row.DateCreated, row.Postotak)
        return jsonify({"data": data})
    else:
        print("No rows found for date range:", from_date_str, "to", to_date_str)
        return jsonify({"error": "No data found"})


from collections import defaultdict

@app.route("/Grupiranje_materiala_table", methods=['POST'])
def grupiranje_materiala_table():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"})

    documentId = request.form.get('documentInput')

    try:
        # Fetch data from the database and create a pandas DataFrame
        grouped_data = TREZ_KALK.query.filter(TREZ_KALK.Ident == documentId).all()
        df = pd.DataFrame([(item.Ident, item.Bruto, item.Debljina, item.Kvaliteta) for item in grouped_data],
                          columns=['Ident', 'Bruto', 'Debljina', 'Kvaliteta'])

        # Group by 'Ident' and sum 'Bruto'
        grouped_df = df.groupby('Ident').agg({'Bruto': 'sum'}).reset_index()

        # Extract display_ident and display_bruto
        display_ident = grouped_df['Ident'].iloc[0] if not grouped_df.empty else None
        display_bruto = grouped_df['Bruto'].iloc[0] if not grouped_df.empty else None

        # Return only display_ident and display_bruto
        return jsonify({'Ident': display_ident, 'Bruto': display_bruto})

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
    else:
        # Handle other roles or unauthorized access
        return render_template('unauthorized.html')

if __name__ == "__main__":
    app.run(debug=True)
