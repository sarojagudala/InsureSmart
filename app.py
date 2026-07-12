from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pickle
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# ===========================
# Load Environment Variables
# ===========================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

# ===========================
# Flask App
# ===========================
app = Flask(__name__)

# ===========================
# Load Machine Learning Model
# ===========================
try:
    with open("insurance_model.pkl", "rb") as file:
        insurance_model = pickle.load(file)
except:
    insurance_model = None

# ===========================
# SQLite Database
# ===========================
DATABASE = "database/insurance.db"

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            age INTEGER,

            gender TEXT,

            income INTEGER,

            bmi REAL,

            smoker TEXT,

            diabetes TEXT,

            blood_pressure TEXT,

            insurance_type TEXT,

            risk_level TEXT,

            premium REAL,

            recommendation TEXT,

            created_at TEXT

        )
    """)

    conn.commit()

    conn.close()

init_db()

# ===========================
# Risk Calculation
# ===========================
def calculate_risk(age, bmi, smoker, diabetes, bp):

    score = 0

    if age >= 55:
        score += 25

    elif age >= 40:
        score += 15

    if bmi >= 30:
        score += 20

    elif bmi >= 25:
        score += 10

    if smoker == "Yes":
        score += 30

    if diabetes == "Yes":
        score += 15

    if bp == "High":
        score += 15

    if score < 25:
        return "Low"

    elif score < 60:
        return "Medium"

    return "High"

# ===========================
# Premium Estimation
# ===========================
def estimate_premium(age, income, risk):

    premium = 5000

    premium += age * 40

    if risk == "Medium":
        premium += 2500

    elif risk == "High":
        premium += 6000

    if income > 1000000:
        premium += 1000

    return round(premium,2)

# ===========================
# Gemini Recommendation
# ===========================
def gemini_recommend(data):

    if model is None:
        return (
            "Gemini API key not configured. "
            "Using local recommendation."
        )

    prompt = f"""

You are an insurance advisor.

Analyze the following customer profile.

Name : {data['name']}

Age : {data['age']}

Gender : {data['gender']}

Income : {data['income']}

BMI : {data['bmi']}

Smoker : {data['smoker']}

Diabetes : {data['diabetes']}

Blood Pressure : {data['blood_pressure']}

Insurance Type : {data['insurance_type']}

Risk Level : {data['risk']}

Estimated Premium : ₹{data['premium']}

Provide

1. Risk explanation

2. Suitable insurance

3. Coverage recommendation

4. Financial advice

5. Healthy lifestyle suggestions

"""

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return str(e)

# ===========================
# Home Page
# ===========================
@app.route("/")

def home():

    return render_template("index.html")
# ===========================
# Predict Insurance
# ===========================
@app.route("/predict", methods=["POST"])
def predict():

    try:
        name = request.form["name"]
        age = int(request.form["age"])
        gender = request.form["gender"]
        income = int(request.form["income"])
        bmi = float(request.form["bmi"])
        smoker = request.form["smoker"]
        diabetes = request.form["diabetes"]
        blood_pressure = request.form["blood_pressure"]
        insurance_type = request.form["insurance_type"]

        # Risk Analysis
        risk = calculate_risk(
            age,
            bmi,
            smoker,
            diabetes,
            blood_pressure
        )

        # Premium Estimation
        premium = estimate_premium(
            age,
            income,
            risk
        )

        # Machine Learning Prediction (optional)
        ml_prediction = "Not Available"

        if insurance_model is not None:

            sample = pd.DataFrame([{
                "Age": age,
                "Income": income,
                "BMI": bmi,
                "Smoker": 1 if smoker == "Yes" else 0,
                "Diabetes": 1 if diabetes == "Yes" else 0,
                "HighBP": 1 if blood_pressure == "High" else 0
            }])

            try:
                prediction = insurance_model.predict(sample)[0]
                ml_prediction = prediction
            except Exception:
                ml_prediction = "Prediction Error"

        # AI Recommendation
        user_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "income": income,
            "bmi": bmi,
            "smoker": smoker,
            "diabetes": diabetes,
            "blood_pressure": blood_pressure,
            "insurance_type": insurance_type,
            "risk": risk,
            "premium": premium
        }

        recommendation = gemini_recommend(user_data)

        # Save History
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO history
            (
                name,
                age,
                gender,
                income,
                bmi,
                smoker,
                diabetes,
                blood_pressure,
                insurance_type,
                risk_level,
                premium,
                recommendation,
                created_at
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            name,
            age,
            gender,
            income,
            bmi,
            smoker,
            diabetes,
            blood_pressure,
            insurance_type,
            risk,
            premium,
            recommendation,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            name=name,
            risk=risk,
            premium=premium,
            prediction=ml_prediction,
            recommendation=recommendation
        )

    except Exception as e:

        return f"Application Error : {e}"


# ===========================
# History Page
# ===========================
@app.route("/history")
def history():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=rows
    )


# ===========================
# Delete History
# ===========================
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# ===========================
# Clear All History
# ===========================
@app.route("/clear")
def clear():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM history")

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# ===========================
# About Page
# ===========================
@app.route("/about")
def about():
    return """
    <h2>InsureSmart</h2>

    <p>
    AI Powered Insurance Recommendation System
    using Flask, Machine Learning and
    Google Gemini AI.
    </p>
    """


# ===========================
# Run Application
# ===========================
if __name__ == "__main__":
    app.run(debug=True)
