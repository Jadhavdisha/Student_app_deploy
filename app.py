from flask import Flask, render_template, request, redirect, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mysecret")

# MongoDB setup (NO ping at import time)
MONGO_URL = os.getenv("MONGO_URL")
client = None
db = None
users = None

if MONGO_URL:
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["student_app"]
        users = db["users"]
        logging.info("MongoDB client initialized.")
    except Exception as e:
        logging.error("MongoDB initialization failed: %s", e)
else:
    logging.error("MONGO_URL not set.")

@app.route('/')
def index():
    return redirect('/login')

# ---------------- REGISTER ----------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if users is None:
        flash("Database unavailable. Try again later.", "danger")
        return render_template("register.html")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return render_template("register.html")

        if users.find_one({"email": email}):
            flash("Email already registered.", "warning")
            return redirect('/login')

        users.insert_one({
            "name": name,
            "email": email,
            "password": password  # hash later
        })

        flash("Account created. Please login.", "success")
        return redirect('/login')

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if users is None:
        flash("Database unavailable.", "danger")
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = users.find_one({"email": email})
        print("USER FROM DB:", user)   # DEBUG

        if not user:
            flash("User not found. Please register.", "danger")
            return render_template("login.html")

        if user["password"] != password:
            flash("Wrong password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = str(user["_id"])
        return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect('/login')

    try:
        user = users.find_one({"_id": ObjectId(session["user_id"])})
    except Exception:
        session.clear()
        flash("Session expired. Please login again.", "danger")
        return redirect('/login')

    courses = [
        {"code": "CSE101", 
         "title": "Introduction to CS",
        "credits": 3},
        {"code": "MAT102",
          "title": "Calculus I", 
          "credits": 4},
        {"code": "PHY103",
          "title": "Physics I",
            "credits": 3},
    ]

    return render_template("dashboard.html", name=user["name"], courses=courses)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect('/login')

# Local only
if __name__ == '__main__':
    app.run(debug=True)
