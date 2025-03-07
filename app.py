import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

# Setup Bcrypt for password hashing and Flask-Login for session management
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

# Secret key for session management
app.secret_key = os.urandom(24)

# 🔑 Set your Mistral API Key here
MISTRAL_API_KEY = "E2jg9R9wmwJBVxFA1GH5LXQRtncxSQ8R"

# ✅ Companies & Job Roles List
COMPANIES = ["Google", "Microsoft", "Amazon", "Facebook", "Apple", "Netflix", "Tesla", "Adobe", "IBM", "Salesforce"]
JOB_ROLES = ["Software Engineer", "Data Scientist", "Machine Learning Engineer", "Frontend Developer",
             "Backend Developer", "Full Stack Developer", "Cybersecurity Analyst", "Cloud Engineer",
             "DevOps Engineer", "AI Researcher"]

# Dummy in-memory database for users
users = {}

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

def generate_question(company, role):
    """Get an interview question from Mistral AI."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": "You are a technical interviewer."},
            {"role": "user", "content": f"Generate a technical interview question for a {role} at {company}."}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "No question generated.")
        else:
            print(f"❌ API Error: {response.status_code}, Response: {response.text}")
            return f"Error: Mistral API returned {response.status_code}."

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {str(e)}")
        return "Error: Failed to connect to Mistral API."

def generate_correct_answer(question):
    """Generate the correct answer using Mistral AI."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": "You are a technical interviewer. Provide the correct answer for the given question."},
            {"role": "user", "content": f"Question: {question}\nProvide the correct answer."}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "No answer generated.")
        else:
            print(f"❌ API Error: {response.status_code}, Response: {response.text}")
            return f"Error: Mistral API returned {response.status_code}."

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {str(e)}")
        return "Error: Failed to connect to Mistral API."

def evaluate_answer(question, user_answer, correct_answer):
    """Evaluate user's answer using Mistral AI."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": "You are an AI that evaluates interview answers and gives feedback."},
            {"role": "user", "content": f"Question: {question}\nUser's Answer: {user_answer}\nCorrect Answer: {correct_answer}\nGive feedback on correctness and improvement suggestions."}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "No feedback generated.")
        else:
            print(f"❌ API Error: {response.status_code}, Response: {response.text}")
            return f"Error: Mistral API returned {response.status_code}."

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {str(e)}")
        return "Error: Failed to connect to Mistral API."

# Routes for registration, login, and logout
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in [user.username for user in users.values()]:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # Hash the password and create the user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = str(len(users) + 1)
        new_user = User(user_id, username, hashed_password)
        users[user_id] = new_user

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        for user in users.values():
            if user.username == username and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("index"))

        flash("Invalid credentials, please try again.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", companies=COMPANIES, roles=JOB_ROLES)

@app.route("/ask_question", methods=["POST"])
def ask_question():
    data = request.get_json()
    company = data.get("company")
    role = data.get("role")

    if not company or not role:
        return jsonify({"error": "Company and role are required"}), 400

    question = generate_question(company, role)
    return jsonify({"question": question})

@app.route("/evaluate_answer", methods=["POST"])
def evaluate():
    data = request.get_json()
    question = data.get("question")
    user_answer = data.get("answer")

    if not question or not user_answer:
        return jsonify({"error": "Question and answer are required"}), 400

    correct_answer = generate_correct_answer(question)
    feedback = evaluate_answer(question, user_answer, correct_answer)

    return jsonify({"correct_answer": correct_answer, "feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
