from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@ 192.168.100.45/MegaMetal'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for favicon.ico
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'
#db = SQLAlchemy(app)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Dummy user data (replace this with a real user authentication system)
users = {
    "admin": {"password": "admin", "role": "admin"},
    "user1": {"password": "password1", "role": "user"}
}

def is_authenticated():
    return "username" in session

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            # Authentication successful, store username in session
            session["username"] = username
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
    role = users[username]["role"]
    return render_template("home.html", username=username, role=role)
@app.route("/about")
def about():
    if not is_authenticated():
        return redirect(url_for("login"))
    username = session["username"]
    role = users[username]["role"]
    return render_template("testing.html", username=username, role=role)

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if not is_authenticated():
        return redirect(url_for("login"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        if users.get(session["username"], {}).get("role") == "admin":
            users[username] = {"password": password, "role": role}
            return redirect(url_for("home"))
        else:
            return "Unauthorized: Only admin users can add new users."
    return render_template("add_user.html")

@app.route("/sign_out")
def sign_out():
    # Clear the session data
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
