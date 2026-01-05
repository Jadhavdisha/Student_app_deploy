from flask import Flask, render_template, request, redirect, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "render-safe-secret"

# ---------------- MONGODB ----------------
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["student_app"]
users = db["users"]

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return redirect("/login")

# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"].lower()
        password = request.form["password"]

        if users.find_one({"email": email}):
            flash("Email already exists")
            return redirect("/login")

        user = users.insert_one({
            "name": name,
            "email": email,
            "password": password
        })

        return redirect(f"/dashboard/{user.inserted_id}")

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        user = users.find_one({"email": email, "password": password})
        if not user:
            flash("Invalid credentials")
            return redirect("/login")

        return redirect(f"/dashboard/{user['_id']}")

    return render_template("login.html")

# -------- DASHBOARD --------
@app.route("/dashboard/<user_id>")
def dashboard(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect("/login")

    courses = [
        {"code": "CSE101", "title": "Intro to CS", "credits": 3},
        {"code": "MAT102", "title": "Calculus I", "credits": 4},
        {"code": "PHY103", "title": "Physics I", "credits": 3}
    ]

    return render_template("dashboard.html", user=user, courses=courses)

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    return redirect("/login")

if __name__ == "__main__":
    app.run()
