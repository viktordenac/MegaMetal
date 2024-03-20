from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Dummy user data (replace this with a real user authentication system)
users = {
    1: {"ID": 1, "username": "admin", "password": "admin", "role": "admin"},
    2: {"username": "user1", "password": "user1", "role": "user"},
    3: {"username": "poslovodja", "password": "123", "role": "poslovodja"},
    4: {"username": "user2", "password": "user2", "role": "user"},
}

def is_authenticated():
    return "user_id" in session

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = int(request.form["user_id"])
        if user_id in users:
            # Authentication successful, store user ID in session
            session["user_id"] = user_id
            return redirect(url_for("home"))
        else:
            # Authentication failed, reload login page with an error message
            return render_template("login.html", error="Invalid user ID.")
    return render_template("login.html", error=None)

@app.route("/home")
def home():
    if not is_authenticated():
        return redirect(url_for("login"))
    user_id = session["user_id"]
    username = users[user_id]["username"]
    role = users[user_id]["role"]
    return render_template("home.html", username=username, role=role)

# @app.route("/about")
# def about():
#     if not is_authenticated():
#         return redirect(url_for("login"))
#     username = session["username"]
#     role = users[username]["role"]
#     return render_template("testing.html", username=username, role=role)

# @app.route("/add_user", methods=["GET", "POST"])
# def add_user():
#     if not is_authenticated():
#         return redirect(url_for("login"))
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         role = request.form["role"]
#         if users.get(session["username"], {}).get("role") == "admin":
#             users[username] = {"password": password, "role": role}
#             return redirect(url_for("home"))
#         else:
#             return "Unauthorized: Only admin users can add new users."
#     return render_template("add_user.html")

@app.route("/sign_out")
def sign_out():
    # Clear the session data
    session.clear()
    return redirect(url_for("login"))

from flask import render_template

@app.route("/time_entry", methods=["GET"])
def time_entry():
    return render_template("testing.html")


if __name__ == "__main__":
    app.run(debug=True)
