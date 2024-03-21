from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
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
    Vrijeme = db.Column(db.FLOAT())
    Kartica = db.Column(db.Numeric(25, 0), primary_key=True)
    Id_rn = db.Column(db.CHAR(50))

class DELOVNI_NALOG(db.Model):
    __tablename__ = 'TRN_RN'
    Id_rn = db.Column(db.CHAR(50), primary_key=True)
    Aktivan = db.Column(db.CHAR(2))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = int(request.form["user_id"])
        employee = TBA_RAD.query.filter_by(Kartica=user_id).first()
        if employee:
            # Authentication successful, store user ID in session
            session["user_id"] = employee.Kartica
            session["username"] = employee.Ime
            return redirect(url_for("evidenca_ur"))
        else:
            # Authentication failed, reload login page with an error message
            return render_template("login.html", error="Invalid user ID.")
    return render_template("login.html", error=None)

@app.route("/home")
def home():
    #TODO Dont forget to remove this comment
    # if not is_authenticated():
    #     return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/evidencaUr")
def evidenca_ur():
    if not is_authenticated():
        return redirect(url_for("login"))
    activities = DELOVNI_NALOG.query.filter_by(Aktivan='1').all()
    # print(activities)
    return render_template("evidencaUr.html", activities=activities)

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
    vrijeme = ure + minute

    datum = datetime.now().date()
    trenutni_cas = datetime.now().time()

    # Calculate izmena based on time
    if trenutni_cas.hour >= 6 and trenutni_cas.hour < 14:
        izmena = 1
    elif trenutni_cas.hour >= 14 and trenutni_cas.hour < 22:
        izmena = 2
    else:
        izmena = 3


    # Create a new TBA_EVID object
    new_entry = TEV_EVID(Datum=datum, Izmena=izmena, Vrijeme=vrijeme, Kartica=kartica, Id_rn=id_rn)

    # Add the new entry to the database session and commit
    db.session.add(new_entry)
    db.session.commit()

    return "Data inserted successfully!"

@app.route("/sign_out")
def sign_out():
    # Clear the session data
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
