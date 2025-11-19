# filename: app.py
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
import requests
import re
import time

API_KEY = "AIzaSyCKCcoI_GT1medjXxglgPCxxlgrXomfS1E"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

app = Flask(__name__)
run_with_ngrok(app)  # Automatically starts ngrok when the app runs

def ask_gemini(message, retry_count=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gemini-2.0-flash",
        "messages": [
            {
                "role": "user",
                "content": f"Respond ONLY in Kannada language. User message: {message}. Give plain text response only, no formatting, no bullets, no asterisks."
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    for attempt in range(retry_count):
        try:
            response = requests.post(BASE_URL, headers=headers, json=body, timeout=30)

            if response.status_code == 429:  # Rate limit
                time.sleep((attempt + 1) * 2)
                continue

            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                result = data["choices"][0]["message"]["content"]
                result = re.sub(r"[*•\-—]", "", result).strip()
                return result
            else:
                return "ಕ್ಷಮಿಸಿ, ನನಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ"

        except requests.exceptions.Timeout:
            if attempt == retry_count - 1:
                return "ಕ್ಷಮಿಸಿ, ಸಮಯ ಮೀರಿದೆ"
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            if attempt == retry_count - 1:
                if "429" in str(e):
                    return "⏳ ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ನಿಮಿಷ ಕಾಯಿರಿ, ಹೆಚ್ಚಿನ ವಿನಂತಿಗಳು"
                return "ದೋಷ ಸಂಭವಿಸಿದೆ"
            time.sleep(1)
        except Exception:
            if attempt == retry_count - 1:
                return "ಕ್ಷಮಿಸಿ, ದೋಷ ಸಂಭವಿಸಿದೆ"
            time.sleep(1)

    return "ಕ್ಷಮಿಸಿ, ದೋಷ ಸಂಭವಿಸಿದೆ"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Please provide a 'message' field"}), 400

    reply = ask_gemini(message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    print("Starting Flask app with ngrok...")
    app.run()
