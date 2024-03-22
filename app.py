from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
#python -m pip install flask_sqlalchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Replace the following with your actual PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:potgresql@192.168.100.216/megametal'

# Initialize SQLAlchemy extension
db = SQLAlchemy(app)

class TBA_RAD(db.Model):
    __tablename__ = 'TBA_RAD'
    Ime = db.Column(db.String(100))
    Kartica = db.Column(db.Numeric(25, 0), primary_key=True)
    Mjesto = db.Column(db.String(10))
    Username = db.Column(db.CHAR(15))
    Password = db.Column(db.CHAR(10))

class TREZ_TIME(db.Model):
    __tablename__ = 'TREZ_TIME'
    JobCode = db.Column(db.CHAR(25), primary_key=True)
    DateCreated = db.Column(db.DateTime)
    Postotak = db.Column(db.REAL)


def is_authenticated():
    return "username" in session

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form_username = request.form["username"]
        form_password = request.form["password"]
        username = TBA_RAD.query.filter_by(Username=form_username).first()

        if username and form_password == str(username.Password):
            # Authentication successful, store username in session
            session["username"] = username.Username
            print(session["username"])
            return redirect(url_for("home"))
        else:
            # Authentication failed, reload login page with an error message
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html", error=None)

@app.route("/home")
def home():
    if not is_authenticated():
        return redirect(url_for("login"))
    username = session["username"]
    return render_template("home.html", Username=username)

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


from flask import request


@app.route("/Potrosnja_materiala")
def potrosnja_materiala():
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template("potrosnja_materiala_grafi.html")

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


@app.route("/sign_out")
def sign_out():
    # Clear the session data
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
