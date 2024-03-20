from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Dummy user data (replace this with a real user authentication system)
users = {
    "admin": {"ID": "1", "password": "admin", "role": "admin"},
    "user1": {"ID": "2", "password": "user1", "role": "user"},
    "poslovodja": {"ID": "3", "password": "123", "role": "poslovodja"},
    "user2": {"ID": "4", "password": "user2", "role": "user"},
}
#users=[1,2,3]
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

@app.route("/login_with_id", methods=["GET", "POST"])
def login_with_id():
    if request.method == "POST":
        user_id = request.form["user_id"]
        print(user_id)
        if user_id in users:  # Check if user data exists
            # Authentication successful, store username in session
            # User found by ID, redirect to home page
            print(user_id)
            return redirect(url_for("home"))
    return render_template("login_with_ID.html", error="Invalid user ID.")



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
