from datetime import datetime
import rdm6300

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "haas#5ess!"  # Change this to a random secret key

def is_authenticated():
    return "user_id" in session

# Replace the following with your actual PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:potgresql@192.168.100.216/megametal'

# Initialize SQLAlchemy extension
db = SQLAlchemy(app)

class TBA_RAD(db.Model):
    __tablename__ = 'TBA_RAD'
    Ime = db.Column(db.String(100))
    Kartica = db.Column(db.Numeric(25, 0), primary_key=True)
    Mjesto = db.Column(db.String(10))

class TEV_EVID(db.Model):
    __tablename__ = 'TEV_EVID'
    Datum = db.Column(db.DATE())
    Izmena = db.Column(db.INT())
    Faza = db.Column(db.CHAR(50))
    Opombe = db.Column(db.CHAR(100))
    Vrijeme = db.Column(db.FLOAT())
    Kartica = db.Column(db.Numeric(25, 0), primary_key=True)
    Id_rn = db.Column(db.CHAR(50))

class TBA_FAZA(db.Model):
    __tablename__ = 'TBA_FAZA'
    Key = db.Column(db.CHAR(2), primary_key=True)
    Test = db.Column(db.CHAR(20))

class DELOVNI_NALOG(db.Model):
    __tablename__ = 'TRN_RN'
    Id_rn = db.Column(db.CHAR(50), primary_key=True)
    Aktivan = db.Column(db.CHAR(2))
    Status = db.Column(db.CHAR(15))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = int(request.form["user_id"])
        employee = TBA_RAD.query.filter_by(Kartica=user_id).first()
        if employee:
            # Authentication successful, store user ID in session
            session["user_id"] = employee.Kartica
            session["username"] = employee.Ime
            session["vloga"] = employee.Mjesto
            return redirect(url_for("evidenca_ur"))
        else:
            # Authentication failed, reload login page with an error message
            return render_template("login.html", error="Invalid user ID.")
    return render_template("login.html", error=None)

@app.route("/evidencaUr")
def evidenca_ur():
    if not is_authenticated():
        return redirect(url_for("login"))
    activities = DELOVNI_NALOG.query.filter_by(Aktivan='1', Status=session["vloga"]).all()
    faze = TBA_FAZA.query.filter_by(Key='V').all()
    faze_values = [faza.Test for faza in TBA_FAZA.query.all()]
    return render_template("evidencaUr.html", radniNalogi=activities, faze=faze)


from flask import jsonify

@app.route("/submitEvidencaUr", methods=["GET", "POST"])
def submit_evidenca_ur():
    if not is_authenticated():
        return redirect(url_for("login"))

    # Get data from the request
    ure = request.form.get('DUre')
    ure = int(ure)
    minute = request.form.get('DMinute')
    minute = int(minute)/60
    kartica = session["user_id"]
    id_rn = request.form.get('Id_rn')
    faza = request.form.get('Faza')
    opombe = request.form.get('Opomba')

    vrijeme = ure + minute
    datum = datetime.now().date()
    trenutni_cas = datetime.now().time()

    # Calculate izmena based on time
    if trenutni_cas.hour >= 6 and trenutni_cas.hour < 15:
        izmena = 1
    elif trenutni_cas.hour >= 15 and trenutni_cas.hour < 23:
        izmena = 2
    else:
        izmena = 3

    if id_rn and vrijeme and faza:
        # Create a new TBA_EVID object
        new_entry = TEV_EVID(Datum=datum, Izmena=izmena, Faza=faza, Opombe=opombe, Vrijeme=vrijeme, Kartica=kartica, Id_rn=id_rn)
        # Add the new entry to the database session and commit
        db.session.add(new_entry)
        db.session.commit()
        return "Data inserted successfully!"
    else:
        return jsonify({"error": "Please select a valid activity"}), 400  # Return a 400 Bad Request status code along with the error message


@app.route("/get_user_id", methods=["GET"])
def get_user_id():
    # # Return the user ID as a JSON response
    # reader = rdm6300.Reader('/dev/ttyS0')
    # print("Please insert an RFID card")
    # while True:
    #     card = reader.read()
    #     if card:
    #         print(f"[{card.value}] read card {card}")
    #
    #         return jsonify({"user_id": card.value})
    #     else:
    #         print("No card detected")
    #         continue
    return jsonify({"user_id": "219052678526"})


@app.route("/sign_out")
def sign_out():
    # Clear the session data
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)