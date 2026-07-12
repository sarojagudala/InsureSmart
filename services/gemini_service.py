import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


def generate_recommendation(
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
        premium
):

    if model is None:
        return """
Gemini API Key not found.

Please create a .env file and add

GEMINI_API_KEY=YOUR_API_KEY
"""

    prompt = f"""
You are an expert Insurance Advisor.

Analyze the customer profile and provide a professional insurance recommendation.

Customer Details

Name: {name}

Age: {age}

Gender: {gender}

Annual Income: ₹{income}

BMI: {bmi}

Smoker: {smoker}

Diabetes: {diabetes}

Blood Pressure: {blood_pressure}

Insurance Type: {insurance_type}

Calculated Risk Level: {risk}

Estimated Premium: ₹{premium}

Generate a detailed report in this format:

1. Customer Risk Summary

2. Risk Explanation

3. Recommended Insurance Policy

4. Suggested Coverage Amount

5. Premium Analysis

6. Benefits of the Policy

7. Financial Planning Advice

8. Health & Lifestyle Recommendations

9. Final Recommendation

Write the response in simple English.
"""

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"Gemini Error: {str(e)}"


# Test the API directly
if __name__ == "__main__":

    result = generate_recommendation(
        name="Saroja",
        age=24,
        gender="Female",
        income=600000,
        bmi=24.5,
        smoker="No",
        diabetes="No",
        blood_pressure="Normal",
        insurance_type="Health",
        risk="Low",
        premium=5200
    )

    print(result)
