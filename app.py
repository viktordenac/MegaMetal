import io
import os
import re
from collections import defaultdict
from datetime import datetime, date, timedelta
import calendar

import holidays
import msoffcrypto
from dateutil.relativedelta import relativedelta

slo_holidays = holidays.SI()  # this is a dict

import pandas as pd
import json

from flask import Flask, render_template, redirect, url_for, send_file, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, exists, text, asc
from io import BytesIO
from sqlalchemy.exc import IntegrityError
from realizirano import Realizirano

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
    Kartica_value = db.Column(db.Numeric(25, 0))
    Mjesto = db.Column(db.CHAR(15))
    Username = db.Column(db.CHAR(15))
    Password = db.Column(db.CHAR(10))
    Datexp = db.Column(db.DateTime())

class TREZ_TIME(db.Model):
    __tablename__ = 'TREZ_TIME'
    JobCode = db.Column(db.CHAR(25), primary_key=True)
    DateCreated = db.Column(db.DateTime)
    Postotak = db.Column(db.REAL)
    Bruto = db.Column(db.REAL)
    Neto = db.Column(db.REAL)

class TREZ_KALK(db.Model):
    __tablename__ = 'TREZ_KALK'
    Ident = db.Column(db.CHAR(10), primary_key=True)
    Id_rn = db.Column(db.Integer, primary_key=True)  # Define additional columns as per your table schema
    Bruto = db.Column(db.REAL)
    Debljina = db.Column(db.INT())
    Kvaliteta = db.Column(db.CHAR(20))  # Adjust data type and length as per your table schema

class TEV_EVID(db.Model):
    __tablename__ = 'TEV_EVID'
    Ime = db.Column(db.CHAR(100))
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

class TBA_PRAVA(db.Model):
    __tablename__ = 'TBA_PRAVA'
    Username = db.Column(db.CHAR(15), primary_key=True)
    Stranice = db.Column(db.CHAR(1000))

class TPRO_PLAN(db.Model):
    __tablename__ = 'TPRO_PLAN'
    KUPEC = db.Column(db.CHAR(100))
    Stari_DN = db.Column(db.CHAR(50))
    OPOMBE = db.Column(db.CHAR(100))
    IDENT_NR = db.Column(db.CHAR(15))
    KLJUCAVNICAR = db.Column(db.CHAR(50))
    KOS = db.Column(db.INT())
    IDRN = db.Column(db.CHAR(20), primary_key=True)
    INDEX = db.Column(db.CHAR(25))
    BARVA = db.Column(db.CHAR(50))
    KONSTRUKCIJA_OD = db.Column(db.DATE())
    KONSTRUKCIJA_DO = db.Column(db.DATE())
    KONSTRUKCIJA_DANI = db.Column(db.INT())
    KONSTRUKCIJA_STATUS = db.Column(db.CHAR(15))
    RAZREZ_OD = db.Column(db.DATE())
    RAZREZ_DO = db.Column(db.DATE())
    RAZREZ_DANI = db.Column(db.INT())
    RAZREZ_STATUS = db.Column(db.CHAR(15))
    MPO_OD = db.Column(db.DATE())
    MPO_DO = db.Column(db.DATE())
    MPO_DANI = db.Column(db.INT())
    MPO_STATUS = db.Column(db.CHAR(15))
    ZBIRANJE_OD = db.Column(db.DATE())
    ZBIRANJE_DO = db.Column(db.DATE())
    ZBIRANJE_DANI = db.Column(db.INT())
    ZBIRANJE_STATUS = db.Column(db.CHAR(15))
    SESTAVLJANJE_OD = db.Column(db.DATE())
    SESTAVLJANJE_DO = db.Column(db.DATE())
    SESTAVLJANJE_DANI = db.Column(db.INT())
    SESTAVLJANJE_STATUS = db.Column(db.CHAR(15))
    VARENJE_OD = db.Column(db.DATE())
    VARENJE_DO = db.Column(db.DATE())
    VARENJE_DANI = db.Column(db.INT())
    VARENJE_STATUS = db.Column(db.CHAR(15))
    ZARENJE_OD = db.Column(db.DATE())
    ZARENJE_DO = db.Column(db.DATE())
    ZARENJE_DANI = db.Column(db.INT())
    ZARENJE_STATUS = db.Column(db.CHAR(15))
    BRUSENJE_OD = db.Column(db.DATE())
    BRUSENJE_DO = db.Column(db.DATE())
    BRUSENJE_DANI = db.Column(db.INT())
    BRUSENJE_STATUS = db.Column(db.CHAR(15))
    KONTR_I_LAK_OD = db.Column(db.DATE())
    KONTR_I_LAK_DO = db.Column(db.DATE())
    KONTR_I_LAK_DANI = db.Column(db.INT())
    KONTR_I_LAK_STATUS = db.Column(db.CHAR(15))
    PESK_I_BARV_OD = db.Column(db.DATE())
    PESK_I_BARV_DO = db.Column(db.DATE())
    PESK_I_BARV_DANI = db.Column(db.INT())
    PESK_I_BARV_STATUS = db.Column(db.CHAR(15))
    MEHANSKA_OBDELAVA_OD = db.Column(db.DATE())
    MEHANSKA_OBDELAVA_DO = db.Column(db.DATE())
    MEHANSKA_OBDELAVA_DANI = db.Column(db.INT())
    MEHANSKA_OBDELAVA_STATUS = db.Column(db.CHAR(15))
    DAT_ISPO = db.Column(db.DATE())
    ISPO_STATUS = db.Column(db.CHAR(15))
    STVARNA_ISPORUKA = db.Column(db.DATE())
    DOG_ISPO = db.Column(db.DATE())
class TBA_KOS(db.Model):
    __tablename__ = 'TBA_KOS'
    Polizdelek = db.Column(db.CHAR(15))
    Neto_tez = db.Column(db.REAL)
    Bruto_tez = db.Column(db.REAL)
    PK = db.Column(db.INT(), primary_key=True)

class TBA_ALAT(db.Model):
    __tablename__ = 'TBA_ALAT'
    PK = db.Column(db.INT(), primary_key=True)
    ALAT = db.Column(db.CHAR(50))
    IDENTIFIKACIJA = db.Column(db.CHAR(50))
    LOKACIJA = db.Column(db.CHAR(50))
    CERTNR = db.Column(db.CHAR(50))
    POSEBNOSTI = db.Column(db.CHAR(50))
    DATUMEXP = db.Column(db.Date())
    DATUMPEXP = db.Column(db.Date())


class TBA_FIX_PL(db.Model):
    __tablename__ = 'TBA_FIX_PL'
    PK = db.Column(db.Integer, primary_key=True)
    GOD = db.Column(db.Numeric)
    KEY = db.Column(db.String)
    MJESEC = db.Column(db.Numeric)
    KW = db.Column(db.Numeric)
    IZNOS = db.Column(db.Float)
    TEZINA = db.Column(db.Float)


class TBA_FIX_REAL(db.Model):
    __tablename__ = 'TBA_FIX_REAL'
    PK = db.Column(db.Integer, primary_key=True)
    GOD = db.Column(db.Numeric)
    KEY = db.Column(db.String)
    MJESEC = db.Column(db.Numeric)
    KW = db.Column(db.Numeric)
    IZNOS = db.Column(db.Float)
    TEZINA = db.Column(db.Float)

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
        if user:
            if user.Datexp != None and user.Datexp != '':
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

@app.route("/potrosnja_materiala_grafi")
def potrosnja_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    stranice_list = session["stranice"]
    return render_template("potrosnja_materiala_grafi.html", stranice_list=stranice_list)

@app.route("/potrosnja_materiala_torta")
def potrosnja_materiala_torta():
    if not is_authenticated():
        return redirect(url_for("login"))
    stranice_list = session["stranice"]
    return render_template("potrosnja_materiala_torta.html", stranice_list=stranice_list)

@app.route("/grupiranje_materiala")
def grupiranje_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    identi = TREZ_KALK.query.with_entities(TREZ_KALK.Ident).distinct().all()
    identi = [row[0] for row in identi]
    stranice_list = session["stranice"]

    return render_template("grupiranje_materiala.html", radniNalogi=identi, stranice_list=stranice_list)

@app.route("/aktivni_nalogi")
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
    stranice_list = session["stranice"]
    return render_template("aktivni_nalogi.html", data=data, unique_values=unique_values, stranice_list=stranice_list)

@app.route("/edit_aktivni_nalogi", methods=['POST'])
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

@app.route('/add_aktivni_nalog', methods=['POST'])
def add_aktivni_nalog():
    # Get data from the form submission
    id_rn = request.form.get('id_rn')
    status = request.form.get('status')
    aktivan = request.form.get('aktivan')

    # Check if a user with the same username already exists
    existing_user = TRN_RN.query.filter_by(Id_rn=id_rn).first()
    if existing_user:
        # User already exists, prompt the user for confirmation
        return jsonify({'prompt': True, 'username': id_rn})

    # User does not exist, proceed with adding the user
    new_nalog = TRN_RN(Id_rn=id_rn,Status=status, Aktivan=aktivan)
    db.session.add(new_nalog)
    db.session.commit()

    return jsonify({'success': True})

def format_date(date_str):
    return date_str.strftime('%Y-%m-%d')


@app.route("/potrošnja_materiala_grafi")
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
                "Postotak": row.Postotak,
                "Bruto": row.Bruto,
            })
            #print(row.JobCode, row.DateCreated, row.Postotak)
        result_dicts = [obj.__dict__ for obj in result]
        df = pd.DataFrame(result_dicts)
        df = df.drop('_sa_instance_state', axis=1)
        column_sum = df['Bruto'].sum()
        df.insert(len(df.columns), 'Udio', df['Bruto'] / column_sum * 100)
        df.insert(len(df.columns), 'Postotak*udio', df['Postotak']/100 * df['Udio']/100)
        column_sum1 = df['Postotak*udio'].sum()
        column_sum1 = (column_sum1 * 100).round(2)
        postotakXudio = column_sum1.astype(str) + "%"
        df['Postotak'] = df['Postotak'].astype(str) + "%"  # Add '%' to the 'Postotak' column
        df['Bruto'] = df['Bruto'].astype(str) + ""  # Round to 3 decimals
        df['Udio'] = df['Udio'].round(2).astype(str) + "%"
        df['Postotak*udio'] = (df['Postotak*udio'] * 100).round(2).astype(str) + "%"

        # Assuming df is your DataFrame
        # Create a new row as a dictionary
        new_df = df[
            ['JobCode', 'DateCreated', 'Postotak', 'Bruto', 'Neto', 'Udio', 'Postotak*udio']]
        new_df['DateCreated'] = new_df['DateCreated'].apply(format_date)
        new_row = pd.DataFrame({'JobCode': ["Suma"],'Bruto': [column_sum],'DateCreated': [''], 'Postotak': [''], 'Neto': [''], 'Udio': [''], 'Postotak*udio': [postotakXudio]})  # Replace 'Column1', 'Column2', value1, and value2 with actual values

        # Append the new row to the DataFrame
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        return jsonify({"data": data, "df": new_df.to_json(orient='records')})
    else:
        #print("No rows found for date range:", from_date_str, "to", to_date_str)
        return jsonify({"error": "No data found"})

@app.route("/grupiranje_materiala_table", methods=['POST'])
def grupiranje_materiala_table():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"})

    documentId = request.form.get('documentInput')

    try:
        # Fetch data from the database
        sumData = TREZ_KALK.query.with_entities(TREZ_KALK.Ident, func.sum(TREZ_KALK.Bruto)).group_by(TREZ_KALK.Ident).all()
        filtered_results = [(row[0], float(row[1])) for row in sumData if row[0] == documentId]
        filtered_bruto = [round((row[1]), 3) for row in filtered_results]  # Round to 3 decimals

        allData = TREZ_KALK.query.with_entities(TREZ_KALK.Ident, TREZ_KALK.Id_rn, func.sum(TREZ_KALK.Bruto)).filter_by(
            Ident=documentId).group_by(TREZ_KALK.Ident, TREZ_KALK.Id_rn).all()

        if not filtered_results and not allData:
            return jsonify({"error": "No data found for the given document ID"})

        # Fetch TBA_KOS data
        id_rn_values = [row[1] for row in allData]
        tba_kos_data = TBA_KOS.query.filter(TBA_KOS.Polizdelek.in_(id_rn_values)).all()

        # Convert TBA_KOS data to a dictionary
        tba_kos_dict = [{'KosId_rn': row.Polizdelek, 'KosNeto': row.Neto_tez, 'KosBruto': row.Bruto_tez} for row in
                        tba_kos_data]

        # Convert allData to a list of dictionaries
        all_data_dict = [{'Ident': row[0], 'Id_rn': row[1], 'Bruto': round((row[2]), 3)} for row in allData]  # Round to 3 decimals

        # Return JSON response
        return jsonify({'AllData': all_data_dict, 'skupnoBruto': filtered_bruto, 'TBA_KOS': tba_kos_dict})

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
    # Handle other roles or unauthorized access
    return redirect(url_for("home"))

@app.route('/home')
def home():
    if not is_authenticated():
        return redirect(url_for("login"))
    # Fetch user permissions from the database
    user_permissions = TBA_PRAVA.query.filter_by(Username=current_user.username).first()

    # Check if user permissions exist
    if user_permissions:
        # Split the 'Stranice' column by ';'
        stranice_list = user_permissions.Stranice.split(';')
        session["stranice"] = stranice_list
        return render_template('home.html', stranice_list=stranice_list)
    else:
        return render_template('unauthorized.html')

@app.route('/user')
def user():
    if not is_authenticated():
        return redirect(url_for("login"))
    # Query all data
    data = TBA_RAD.query.all()

    unique_values = {}
    for column in TBA_RAD.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    return render_template('add_user.html', data=data, unique_values=unique_values, stranice_list=session["stranice"])

@app.route('/add_or_edit_user', methods=['POST'])
def add_or_edit_user():
    # Get data from the form submission
    kartica = request.form.get('kartica')

    # Check if a user with the provided Kartica already exists
    existing_user = TBA_RAD.query.filter_by(Kartica=kartica).first()
    if existing_user:
        # print(existing_user.Username)
        # User already exists, return a JSON response indicating the existence and providing the username
        return jsonify({'exists': True, 'username': existing_user.Username})
    else:
        # print("User does not exist.")
        # User does not exist, proceed with adding the user
        return jsonify({'exists': False})


@app.route('/add_user', methods=['POST'])
def add_user():
    # Get data from the form submission
    name = request.form.get('name')
    username = request.form.get('username')
    kartica = request.form.get('kartica')
    novaKartica = request.form.get('novaKartica')
    mjesto = request.form.get('mjesto')
    password = request.form.get('password')

    if (request.form.get('datexp') != ''):
        datexp = request.form.get('datexp')
    else:
        datexp = None

    # Check if a user with the same Kartica already exists
    existing_user = TBA_RAD.query.filter_by(Kartica=kartica).first()
    if existing_user:
        # User already exists, return an error response
        return jsonify({'success': False, 'error': 'User already exists.'})

    # User does not exist, proceed with adding the user
    new_user = TBA_RAD(Ime=name, Kartica=kartica, Kartica_value=novaKartica, Mjesto=mjesto, Username=username, Password=password, Datexp=datexp)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        # Handle any integrity errors that occur during user creation
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to add user.'}), 500

@app.route('/edit_user', methods=['POST'])
def edit_user():
    # Get data from the form submission
    kartica = request.form.get('kartica')
    # Retrieve other form data as needed

    user = TBA_RAD.query.filter_by(Kartica=kartica).first()
    if user:
        user.Ime = request.form.get('name')
        user.Username = request.form.get('username')
        user.Kartica = request.form.get('kartica')
        user.Kartica_value = request.form.get('novaKartica')
        user.Mjesto = request.form.get('mjesto')
        user.Password = request.form.get('password')
        if (request.form.get('datexp') != ''):
            user.Datexp = request.form.get('datexp')
        else:
            user.Datexp = None
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'User not found.'}), 404


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        # Get the kartica to delete from the request
        kartica = request.json.get('kartica')

        # Check if the user exists
        user = TBA_RAD.query.filter_by(Kartica=kartica).first()
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

    # Query all data
    data = TEV_EVID.query.all()

    unique_values = {}
    for column in TEV_EVID.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if
                                      getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    return render_template('evidenca_ur.html', data=data, unique_values=unique_values, stranice_list=session["stranice"])

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
    return render_template('planiranje_pripravnega_dela.html', stranice_list=session["stranice"])


from collections import defaultdict


from collections import defaultdict

@app.route('/planiranjePripravnegaDelaLoad', methods=['GET'])
def planiranjePripravnegaDelaLoad():
    import datetime
    if not is_authenticated():
        return redirect(url_for("login"))

    try:
        # Fetch column names from the TPRO_PLAN table
        column_names = TPRO_PLAN.__table__.columns.keys()

        # Group columns by their common prefix
        column_groups = []

        for column in column_names:
            prefix = column.split("_")[0]  # Extract the prefix
            found = False
            # Check if the prefix already exists in column_groups
            for group in column_groups:
                if group['prefix'] == prefix:
                    surfix = column.rsplit("_", 1)[1]
                    group['columns'].append(surfix)
                    found = True
                    break
            # If the prefix doesn't exist, create a new group
            if not found:
                parts = column.split("_")
                if len(parts) > 1:
                    surfix = "_".join(parts[1:])
                else:
                    surfix = parts[0]
                column_groups.append({'prefix': prefix, 'columns': [surfix]})

        # for group in column_groups:
        #     print(group['prefix'], group['columns'])

        # Fetch rows from the TPRO_PLAN table
        rows = TPRO_PLAN.query.order_by(asc(TPRO_PLAN.IDRN)).all()
        user_role = session["role"]
        # Check if rows are fetched
        if not rows:
            return jsonify({'error': 'No data found in the TPRO_PLAN table.'}), 404

        # Convert rows to a list of lists for JSON serialization
        data = []
        for row in rows:
            formatted_row = []
            for column in column_names:
                value = getattr(row, column)
                if isinstance(value, datetime.date):
                    # Format datetime objects to dd.mm.yyyy
                    value = value.strftime('%d.%m.%Y')
                formatted_row.append(value)
            data.append(formatted_row)

        # Return the JSON response with column groups
        return jsonify({'column_groups': column_groups, 'data': data, 'role': user_role})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Route to handle submitting updated data
def parse_date(date_str):
    import datetime
    parts = date_str.split('/')
    if len(parts) == 3:
        month, day, year = map(int, parts)
        # Validate day against the number of days in the month
        max_days = calendar.monthrange(year, month)[1]
        if 1 <= day <= max_days:
            # Adjust month by subtracting 1 for zero-based indexing
            return datetime.datetime(year, month, day)
        else:
            # Handle invalid day value
            return None
    else:
        # Handle invalid date format
        return None


def get_next_valid_date(start_date, add_days=None):
    weekend_days = [5, 6]  # Saturday is 5, Sunday is 6

    next_day = start_date
    if add_days is None:
        next_day += timedelta(days=1)
        while next_day.weekday() in weekend_days or next_day in slo_holidays:
            next_day += timedelta(days=1)
    else:
        # Iterate over each day to be added
        next_day += timedelta(days=-1)
        for _ in range(add_days):
            # Add a day and check if it's a weekend or holiday
            next_day += timedelta(days=1)
            while next_day.weekday() in weekend_days or next_day in slo_holidays:
                next_day += timedelta(days=1)
    return next_day


@app.route('/planiranjePripravnegaDelaUpdate', methods=['POST'])
def update_planiranje_pripravnega_Dela():
    import datetime
    print(session["name"])
    updated_data = request.json
    podatki_stranice = updated_data['data']
    id_rn = updated_data['data'][6]
    record = TPRO_PLAN.query.filter_by(IDRN=id_rn).first()
    record_list = []
    for column in record.__table__.columns:
        record_list.append(getattr(record, column.name))
    from decimal import Decimal
    modified_record_list = []
    for item in record_list:
        if isinstance(item, Decimal):
            modified_record_list.append(int(item))  # Convert Decimal to int
        elif isinstance(item, datetime.date):
            try:
                modified_record_list.append(item.strftime('%d/%m/%Y'))  # Format date
            except:
                modified_record_list.append(item.strftime('%m/%d/%Y'))  # Format date
        else:
            modified_record_list.append(item)
    record_titles = []
    differences = [i for i, (x, y) in enumerate(zip(podatki_stranice, modified_record_list)) if str(x) != str(y)]
    print("Indexes with different values:", differences)
    for index in differences[:]:  # using [:] to create a copy of the list to avoid modifying it while iterating
        if str(podatki_stranice[index]) == '':
            differences.remove(index)
    different_value=podatki_stranice[differences[0]]
    list_to_change_od=[9,13,17,21,25,29,33,37,41,45,49]
    list_to_change_do = [10,14,18,22,26,30,34,38,42,46,50]
    filtered_list_od = [x for x in list_to_change_od if x >= differences[0]]
    counter=0
    list_dani=[11,15,19,23,27,31,35,39,43,47,51,53]
    list_to_change_status = [12,16,20,24,28,32,36,40,44,48,52,54]
    mjenjan=0
    indexes = [9,10,13,14,17,18,21,22,25,26,29,30,33,34,37,38,41,42,45,46,49,50]
    date_format = "%d/%m/%Y"
    # Ako je izmjenjen STATUS
    if differences[0] in list_to_change_status:
        modified_record_list=podatki_stranice
    # Ako je izmjenjen datum OD
    if differences[0] in list_to_change_od:
        for i in filtered_list_od:
            if modified_record_list[i+2]==0:
                modified_record_list[i]=modified_record_list[i-3]
                modified_record_list[i+1]=modified_record_list[i-3]
                modified_record_list[i + 3]='J'
                continue
            if counter==0:
                try:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i], date_format)+ timedelta(modified_record_list[i+2]-1)
                except:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i], "%m/%d/%Y")+ timedelta(modified_record_list[i+2]-1)
                while new_date_object_do.weekday() >= 5 or new_date_object_do in slo_holidays:
                    new_date_object_do += timedelta(days=1)
                modified_record_list[i]=podatki_stranice[i]
                modified_record_list[i+1]=new_date_object_do
                counter+=1
            else:
                new_date_object_od=(modified_record_list[i-3])+ timedelta(days=1)#  + timedelta(modified_record_list[i+2]-1)
                while new_date_object_od.weekday() >= 5 or new_date_object_od in slo_holidays:
                    new_date_object_od += timedelta(days=1)
                new_date_object_do=new_date_object_od+ timedelta(modified_record_list[i+2]-1)
                while new_date_object_do.weekday() >= 5 or new_date_object_do in slo_holidays:
                    new_date_object_do += timedelta(days=1)
                modified_record_list[i]=new_date_object_od
                modified_record_list[i+1]=new_date_object_do
                counter+=1
    # Ako je izmjenjen datum DO
    if differences[0] in list_to_change_do:
        for i in list_to_change_do:
            if modified_record_list[i+1]==0:
                modified_record_list[i]=modified_record_list[i-4]
                modified_record_list[i-1]=modified_record_list[i-4]
                modified_record_list[i + 2]='J'
                continue
            if counter==0:
                date_format = "%d/%m/%Y"
                try:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i], date_format)
                except:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i], "%m/%d/%Y")
                while new_date_object_do.weekday() >= 5 or new_date_object_do in slo_holidays:
                    new_date_object_do += timedelta(days=1)
                modified_record_list[i]=new_date_object_do
                counter+=1
            else:
                new_date_object_od=(modified_record_list[i-4])+ timedelta(days=1)
                while new_date_object_od.weekday() >= 5 or new_date_object_od in slo_holidays:
                    new_date_object_od += timedelta(days=1)
                new_date_object_do=new_date_object_od+ timedelta(modified_record_list[i+1]-1)
                while new_date_object_do.weekday() >= 5 or new_date_object_do in slo_holidays:
                    new_date_object_do += timedelta(days=1)
                modified_record_list[i-1]=new_date_object_od
                modified_record_list[i]=new_date_object_do
                counter+=1
    # Ako je izmjenjen datum DOSTAVE
    if differences[0]==53:
        mjenjan=1
        modified_record_list[53]=podatki_stranice[53]
        for i in reversed(indexes):
            if i % 2 == 0:
                try:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i+3], date_format)-timedelta(days=1)
                except:
                    new_date_object_do=datetime.datetime.strptime(podatki_stranice[i+3], "%m/%d/%Y")-timedelta(days=1)
                while new_date_object_do.weekday() >= 5 or new_date_object_do in slo_holidays:
                    new_date_object_do -= timedelta(days=1)
                modified_record_list[i] =new_date_object_do
            if i % 2 == 1:
                new_date_object_od=modified_record_list[i+1] - timedelta(modified_record_list[i+2]-1)
                while new_date_object_od.weekday() >= 5 or new_date_object_od in slo_holidays:
                    new_date_object_od -= timedelta(days=1)
                modified_record_list[i] = new_date_object_od

    zeros_positions = []

    # Ako je dan=0 vrati datume na None
    for i in list_dani:
        if modified_record_list[i] == 0:
            zeros_positions.append(i)
            if i > 0:
                modified_record_list[i - 1] = None
                modified_record_list[i - 2] = None
    filtered_indexes = [x for x in indexes if x >= differences[0]]

    # update datum isporuke
    if mjenjan==0:
        for idx in indexes:
            try:
                modified_record_list[idx] = datetime.datetime.strptime(modified_record_list[idx], '%d/%m/%Y')
            except:
                print("")
        selected_dates = [modified_record_list[i] for i in filtered_indexes if isinstance(modified_record_list[i], datetime.datetime)]
        # Find the maximum date
        max_date = max(selected_dates)
        modified_record_list[53]=max_date+timedelta(days=1)

    if 1==1:
        try:
            # Dynamically assign values from the list to model attributes
            for attr, value in zip(TPRO_PLAN.__table__.columns.keys(), modified_record_list):
                setattr(record, attr, value)
            db.session.commit()
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({"message": "Data updated successfully"})


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
    return render_template('kapaciteta.html', stranice_list=session["stranice"])

@app.route('/izmene', methods=['GET'])
def izmene():
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template('izmene.html', stranice_list=session["stranice"])

@app.route('/editIzmene', methods=['POST'])
def edit_izmene():
    if not is_authenticated():
        return redirect(url_for("login"))

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
    stranice_list = session["stranice"]
    return render_template('verzugs_lista.html', stranice_list=stranice_list)

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

@app.route('/user_roles')
def user_roles():
    if not is_authenticated():
        return redirect(url_for("login"))

    unique_values = {}

    sql_query = """
                    SELECT DISTINCT "Username" 
                    FROM "TBA_RAD" 
                    WHERE "Username" NOT IN (SELECT "Username" FROM "TBA_PRAVA" WHERE "Username" IS NOT NULL)
                    """
    result = db.session.execute(text(sql_query))
    new_usernames = [row[0] for row in result]

    sql_query = """
                        SELECT DISTINCT "Username" 
                        FROM "TBA_PRAVA" 
                        WHERE "Username" NOT IN (SELECT "Username" FROM "TBA_RAD" WHERE "Username" IS NOT NULL)
                        """
    result = db.session.execute(text(sql_query))
    old_usernames = [row[0] for row in result]

    # If there are new usernames, you may need to insert them into TBA_RAD

    # Log to verify the new usernames
    print("Old Usernames:", old_usernames)
    print("New Usernames:", new_usernames)
    for username in new_usernames:
        new_entry = TBA_PRAVA(Username=username)
        db.session.add(new_entry)
        try:
            db.session.commit()
        except IntegrityError:
            # Handle if the username already exists (optional)
            db.session.rollback()

    for username in old_usernames:
        user = TBA_PRAVA.query.filter_by(Username=username).first()
        if user:
            db.session.delete(user)
        try:
            db.session.commit()
        except IntegrityError:
            # Handle if the username already exists (optional)
            db.session.rollback()

    data = TBA_PRAVA.query.filter(TBA_PRAVA.Username != "None").all()

    unique_values = {}
    for column in TBA_PRAVA.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    return render_template('user_roles.html', data=data, unique_values=unique_values, stranice_list=session["stranice"])

@app.route('/update_privileges', methods=['POST'])
def update_privileges():
    try:
        data = request.json
        username = data['username']
        privileges = data['privileges']
        stranice_string = ';'.join(privileges)
        user = TBA_PRAVA.query.filter_by(Username=username).first()
        if user:
            user.Stranice = stranice_string
            db.session.commit()
        else:
            return jsonify({'error': "FAILED UPDATE"}), 400
        return 'Success'
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/edit_user_role', methods=['POST'])
def edit_user_role():
    if not is_authenticated():
        return redirect(url_for("login"))

@app.route('/MM2Alat', methods=['GET'])
def MM2Alat():
    if not is_authenticated():
        return redirect(url_for("login"))
        # Query all data
    data = TBA_ALAT.query.order_by(TBA_ALAT.DATUMPEXP).all()

    unique_values = {}
    for column in TBA_ALAT.__table__.columns:
        column_name = column.name
        unique_values[column_name] = [getattr(row, column_name) for row in data if
                                      getattr(row, column_name) is not None]
        # Filter out duplicates and sort
        unique_values[column_name] = sorted(set(unique_values[column_name]))
    return render_template('MM2_alat.html', data=data, unique_values=unique_values, stranice_list=session["stranice"])

@app.route('/add_or_edit_alat', methods=['POST'])
def add_or_edit_alat():
    # Get data from the form submission
    pk = request.form.get('PK')

    # Check if a user with the provided Kartica already exists
    try:
        existing_alat = TBA_ALAT.query.filter_by(PK=pk).first()
        if existing_alat:
            return jsonify({'success': False, 'error': 'User already exists.'})
    except:
        return jsonify({'exists': False})

@app.route('/add_alat', methods=['POST'])
def add_alat():
    # Get data from the form submission
    pk = request.form.get('PK')
    alat = request.form.get('alat')
    identifikacija = request.form.get('identifikacija')
    lokacija = request.form.get('lokacija')
    certnr = request.form.get('certnr')
    posebnosti = request.form.get('posebnosti')
    datumExp = request.form.get('datumExp')
    datumPExp = request.form.get('datumPExp')
    if (pk == ''):
        pk = 0

    # Check if a user with the same Kartica already exists
    try:
        existing_alat = TBA_ALAT.query.filter_by(PK=pk).first()
        if existing_alat:
            return jsonify({'success': False, 'error': 'User already exists.'})
    except:
        return jsonify({'success': False, 'error': 'User already exists.'})

    # User does not exist, proceed with adding the user
    new_alat = TBA_ALAT(ALAT=alat, IDENTIFIKACIJA=identifikacija, LOKACIJA=lokacija, CERTNR=certnr, POSEBNOSTI=posebnosti, DATUMEXP=datumExp, DATUMPEXP=datumPExp)
    try:
        db.session.add(new_alat)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        # Handle any integrity errors that occur during user creation
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to add user.'}), 500

@app.route('/edit_alat', methods=['POST'])
def edit_alat():
    # Get data from the form submission
    alat = request.form.get('alat')
    # Retrieve other form data as needed

    alat = TBA_ALAT.query.filter_by(ALAT=alat).first()
    if alat:
        alat.KOLICINA = request.form.get('kolicina')
        alat.DATUMEXP = request.form.get('datumExp')
        alat.DATUMPEXP = request.form.get('datumPExp')
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'User not found.'}), 404


@app.route('/delete_alat', methods=['POST'])
def delete_alat():
    if request.method == 'POST':
        # Get the kartica to delete from the request
        pk = request.json.get('PK')

        # Check if the user exists
        try:
            alat = TBA_ALAT.query.filter_by(PK=pk).first()
            if alat:
                # Delete the user from the database
                db.session.delete(alat)
                db.session.commit()
                return jsonify({'success': True})
            else:
                # Return a message indicating that the user does not exist
                return jsonify({'success': False, 'error': 'User not found.'}), 404
        except Exception as e:
            # Handle any errors that occur during deletion
            return jsonify({'success': False, 'error': 'Failed to delete user.'}), 500


podatkiMesec = 0
podatkiKW = 0

@app.route('/fix-plan-navigation')
def fix_plan_navigation():
    global podatkiMesec, podatkiKW
    if not is_authenticated():
        return redirect(url_for("login"))

    try:
        decrypted_workbook = io.BytesIO()
        with open('//192.168.100.216/Users/ivan.tonkic/Desktop/Share/Verzugs_liste/Updated_Orders_Invoices_analize_v5.xlsx', 'rb') as file:
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password='mega')
            office_file.decrypt(decrypted_workbook)

        shipping_data = pd.read_excel(decrypted_workbook, sheet_name='Orders', dtype={'BT': str}, skiprows=[1, 2, 3])

        columns_to_extract = ['Unnamed: 7', 'Unnamed: 95', 'Unnamed: 42', 'Unnamed: 11', 'Unnamed: 13']
        extracted_df = shipping_data[columns_to_extract].copy()

        filtered_df = extracted_df[pd.to_datetime(extracted_df['Unnamed: 95'], errors='coerce', format='%Y-%m-%d').notnull() &
                                   ~extracted_df['Unnamed: 7'].str.contains('STORNO', na=False) &
                                   ~extracted_df['Unnamed: 7'].str.contains('PRENOS', na=False)]

        rows_with_zeros = filtered_df[filtered_df['Unnamed: 42'] == '00:00:00']
        filtered_df.loc[:, 'Unnamed: 42'] = pd.to_datetime(filtered_df['Unnamed: 42'])
        filtered_df = filtered_df[filtered_df['Unnamed: 42'] >= pd.to_datetime('2024-01-01')]

        filtered_df.loc[:, 'Unnamed: 7'] = filtered_df['Unnamed: 7'].apply(lambda x: '-'.join(str(x).split('-')) if re.match(r'^\d+-\d+-\d+$', str(x)) else str(x))
        #MESEC
        filtered_df.loc[:, 'Unnamed: 42'] = pd.to_datetime(filtered_df['Unnamed: 42'])
        filtered_df['Month'] = filtered_df['Unnamed: 42'].dt.month
        filtered_df['Value'] = filtered_df['Unnamed: 11']
        filtered_df.loc[:, 'Unnamed: 7'] = pd.to_datetime(filtered_df['Unnamed: 7'], errors='coerce',
                                                          format='mixed').dt.strftime('%d.%m.%Y')
        podatkiMesec = filtered_df.groupby('Month')['Value'].sum().reset_index()  # po mjesecu
        podatkiMesec = podatkiMesec.to_dict(orient='records')
        #KW
        filtered_df['KW'] = filtered_df['Unnamed: 13']
        filtered_df['Value'] = filtered_df['Unnamed: 11']
        podatkiKW = filtered_df.groupby('KW')['Value'].sum().reset_index()  # po KW
        podatkiKW = podatkiKW.to_dict(orient='records')
    except Exception as e:
        return f"An error occurred: {str(e)}"
    return render_template('fix_plan.html', stranice_list=session["stranice"])


@app.route('/fix-plan')
def fix_plan():
    global podatkiMesec, podatkiKW

    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401

    # Get the status parameter from the request
    status = request.args.get('status', default='Mesec')  # Default value is '1' if parameter is not provided

    try:
        data_str = ""
        if status == 'Mesec':
            data_str = podatkiMesec
        elif status == 'KW':
            data_str = podatkiKW

        return jsonify({'data': data_str})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fix-plan-data')
def fix_plan_data():
    value = request.args.get('month')
    status = request.args.get('status')
    try:
        decrypted_workbook = io.BytesIO()
        with open(
                '//192.168.100.216/Users/ivan.tonkic/Desktop/Share/Verzugs_liste/Updated_Orders_Invoices_analize_v5.xlsx',
                'rb') as file:
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password='mega')
            office_file.decrypt(decrypted_workbook)

        shipping_data = pd.read_excel(decrypted_workbook, sheet_name='Orders', dtype={'BT': str}, skiprows=[1, 2, 3])

        columns_to_extract = ['Unnamed: 7', 'Unnamed: 95', 'Unnamed: 42', 'Unnamed: 11', 'Unnamed: 13']
        extracted_df = shipping_data[columns_to_extract].copy()

        filtered_df = extracted_df[
            pd.to_datetime(extracted_df['Unnamed: 95'], errors='coerce', format='%Y-%m-%d').notnull() &
            ~extracted_df['Unnamed: 7'].str.contains('STORNO', na=False) &
            ~extracted_df['Unnamed: 7'].str.contains('PRENOS', na=False)]

        rows_with_zeros = filtered_df[filtered_df['Unnamed: 42'] == '00:00:00']
        filtered_df.loc[:, 'Unnamed: 42'] = pd.to_datetime(filtered_df['Unnamed: 42'])
        filtered_df = filtered_df[filtered_df['Unnamed: 42'] >= pd.to_datetime('2024-01-01')]

        # Format date
        grouped_df = ""
        filtered_df.loc[:, 'Unnamed: 7'] = filtered_df['Unnamed: 7'].apply(
            lambda x: '-'.join(str(x).split('-')) if re.match(r'^\d+-\d+-\d+$', str(x)) else str(x))
        if status == 'Month':
            filtered_df['Month'] = filtered_df['Unnamed: 42'].dt.month.astype(str)
            filtered_df_id = filtered_df.loc[filtered_df['Month'] == str(value), 'Unnamed: 7']
            filtered_df['ID'] = filtered_df_id
            filtered_df_value = filtered_df.loc[filtered_df['Month'] == str(value), 'Unnamed: 11']
            filtered_df['Value'] = filtered_df_value
            filtered_df.loc[:, 'Unnamed: 7'] = pd.to_datetime(filtered_df['Unnamed: 7'], errors='coerce',
                                                              format='mixed').dt.strftime('%d.%m.%Y')
            grouped_df = pd.DataFrame({
                'ID': filtered_df_id.values,
                'Value': filtered_df_value.values
            })
        elif status == 'KW':
            filtered_df_id = filtered_df.loc[filtered_df['Unnamed: 13'] == value, 'Unnamed: 7']
            filtered_df['ID'] = filtered_df_id
            # Filter 'Value' column
            filtered_df_value = filtered_df.loc[filtered_df['Unnamed: 13'] == value, 'Unnamed: 11']
            filtered_df['Value'] = filtered_df_value
            # Assigning only 'KW' and 'Value' columns to grouped_df
            grouped_df = pd.DataFrame({
                'ID': filtered_df_id.values,
                'Value': filtered_df_value.values
            })
        data_str = grouped_df.to_dict(orient='records')

        json_data = json.dumps(data_str)
        return json_data
    except Exception as e:
        return f"An error occurred: {str(e)}"


"""--------------------------------------------------------------------"""
@app.route("/compare_data_mj")
def compare_data_mj():
    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Calculate the start and end weeks of the current month
    start_week = datetime(current_year, current_month, 1).isocalendar()[1]
    end_week = datetime(current_year, current_month, 1).replace(day=28).isocalendar()[1]

    # Query data from TBA_FIX_PL where MJESEC is null and KW is between start_week and end_week
    pl_data = db.session.query(TBA_FIX_PL.MJESEC, TBA_FIX_PL.IZNOS, TBA_FIX_PL.TEZINA).filter(
        TBA_FIX_PL.KW.is_(None)
    ).all()

    # Query data from TBA_FIX_REAL where MJESEC is null and KW is between start_week and end_week
    real_data = db.session.query(TBA_FIX_REAL.MJESEC, TBA_FIX_REAL.IZNOS, TBA_FIX_REAL.TEZINA).filter(
        TBA_FIX_REAL.KW.is_(None)
    ).all()

    # Sort data by KW values
    pl_data.sort(key=lambda x: x[0])
    real_data.sort(key=lambda x: x[0])

    # Extract KW, IZNOS, and TEZINA values from both tables
    pl_kw_values = [item[0] for item in pl_data]
    pl_iznos_values = [item[1] for item in pl_data]
    pl_tezina_values = [item[2] for item in pl_data]

    real_kw_values = [item[0] for item in real_data]
    real_iznos_values = [item[1] for item in real_data]
    real_tezina_values = [item[2] for item in real_data]

    stranice_list = session["stranice"]
    return render_template("General/compare_data_mj.html", pl_kw_values=pl_kw_values, pl_iznos_values=pl_iznos_values,
                           pl_tezina_values=pl_tezina_values, real_kw_values=real_kw_values,
                           real_iznos_values=real_iznos_values, real_tezina_values=real_tezina_values,
                           stranice_list=stranice_list)


@app.route("/filter_data_mj", methods=["POST"])
def filter_data_mj():
    start_week = request.form.get("startWeek")
    end_week = request.form.get("endWeek")

    # Query data from TBA_FIX_PL where KW is between start_week and end_week
    pl_data = db.session.query(TBA_FIX_PL.MJESEC, TBA_FIX_PL.IZNOS, TBA_FIX_PL.TEZINA).filter(
        TBA_FIX_PL.KW.is_(None)    ).all()

    # Query data from TBA_FIX_REAL where KW is between start_week and end_week
    real_data = db.session.query(TBA_FIX_REAL.MJESEC, TBA_FIX_REAL.IZNOS, TBA_FIX_REAL.TEZINA).filter(
        TBA_FIX_REAL.KW.is_(None)    ).all()

    # Sort data by KW values
    pl_data.sort(key=lambda x: x[0])
    real_data.sort(key=lambda x: x[0])

    # Extract KW, IZNOS, and TEZINA values from both tables
    pl_kw_values = [item[0] for item in pl_data]
    pl_iznos_values = [item[1] for item in pl_data]
    pl_tezina_values = [item[2] for item in pl_data]

    real_kw_values = [item[0] for item in real_data]
    real_iznos_values = [item[1] for item in real_data]
    real_tezina_values = [item[2] for item in real_data]

    # Construct JSON response
    filtered_data = {
        "labels": pl_kw_values,  # Use KW values as labels
        "plIznosValues": pl_iznos_values,
        "realIznosValues": real_iznos_values,
        "plTezinaValues": pl_tezina_values,
        "realTezinaValues": real_tezina_values
    }

    return jsonify(filtered_data)


@app.route("/compare_data")
def compare_data():
    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Calculate the start and end weeks of the current month
    start_week = datetime(current_year, current_month, 1).isocalendar()[1]
    end_week = datetime(current_year, current_month, 1).replace(day=28).isocalendar()[1]

    # Query data from TBA_FIX_PL where MJESEC is null and KW is between start_week and end_week
    pl_data = db.session.query(TBA_FIX_PL.KW, TBA_FIX_PL.IZNOS, TBA_FIX_PL.TEZINA).filter(
        TBA_FIX_PL.MJESEC.is_(None),
        TBA_FIX_PL.KW.between(start_week, end_week)
    ).all()

    # Query data from TBA_FIX_REAL where MJESEC is null and KW is between start_week and end_week
    real_data = db.session.query(TBA_FIX_REAL.KW, TBA_FIX_REAL.IZNOS, TBA_FIX_REAL.TEZINA).filter(
        TBA_FIX_REAL.MJESEC.is_(None),
        TBA_FIX_REAL.KW.between(start_week, end_week)
    ).all()

    # Sort data by KW values
    pl_data.sort(key=lambda x: x[0])
    real_data.sort(key=lambda x: x[0])

    # Extract KW, IZNOS, and TEZINA values from both tables
    pl_kw_values = [item[0] for item in pl_data]
    pl_iznos_values = [item[1] for item in pl_data]
    pl_tezina_values = [item[2] for item in pl_data]

    real_kw_values = [item[0] for item in real_data]
    real_iznos_values = [item[1] for item in real_data]
    real_tezina_values = [item[2] for item in real_data]

    stranice_list = session["stranice"]
    return render_template("General/compare_data.html", pl_kw_values=pl_kw_values, pl_iznos_values=pl_iznos_values,
                           pl_tezina_values=pl_tezina_values, real_kw_values=real_kw_values,
                           real_iznos_values=real_iznos_values, real_tezina_values=real_tezina_values,
                           stranice_list=stranice_list)


@app.route("/filter_data", methods=["POST"])
def filter_data():
    start_week = request.form.get("startWeek")
    end_week = request.form.get("endWeek")

    # Query data from TBA_FIX_PL where KW is between start_week and end_week
    pl_data = db.session.query(TBA_FIX_PL.KW, TBA_FIX_PL.IZNOS, TBA_FIX_PL.TEZINA).filter(
        TBA_FIX_PL.MJESEC.is_(None),
        TBA_FIX_PL.KW.between(start_week, end_week)
    ).all()

    # Query data from TBA_FIX_REAL where KW is between start_week and end_week
    real_data = db.session.query(TBA_FIX_REAL.KW, TBA_FIX_REAL.IZNOS, TBA_FIX_REAL.TEZINA).filter(
        TBA_FIX_REAL.MJESEC.is_(None),
        TBA_FIX_REAL.KW.between(start_week, end_week)
    ).all()

    # Sort data by KW values
    pl_data.sort(key=lambda x: x[0])
    real_data.sort(key=lambda x: x[0])

    # Extract KW, IZNOS, and TEZINA values from both tables
    pl_kw_values = [item[0] for item in pl_data]
    pl_iznos_values = [item[1] for item in pl_data]
    pl_tezina_values = [item[2] for item in pl_data]

    real_kw_values = [item[0] for item in real_data]
    real_iznos_values = [item[1] for item in real_data]
    real_tezina_values = [item[2] for item in real_data]

    # Construct JSON response
    filtered_data = {
        "labels": pl_kw_values,  # Use KW values as labels
        "plIznosValues": pl_iznos_values,
        "realIznosValues": real_iznos_values,
        "plTezinaValues": pl_tezina_values,
        "realTezinaValues": real_tezina_values
    }

    return jsonify(filtered_data)


@app.route("/refresh_fix_plan")
def refresh_fix_plan():
    print("Refreshing data...")
    os.system(r"C:\Users\ivan.tonkic\Desktop\Mega_metal\fix_plan\Fix_plan.bat")
    return jsonify({'success': True})

"""--------------------------------------------------------------------"""


def replace_nan(data):
    return [[cell if not pd.isna(cell) else None for cell in row] for row in data]

if __name__ == "__main__":
    #from waitress import serve
    #serve(app, host='192.168.100.216', port=5000)
    app.run(host='192.168.100.37', port=5000)
    app.run(debug=True)
