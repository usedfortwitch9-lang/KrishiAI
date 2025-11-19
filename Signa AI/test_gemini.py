import google.generativeai as genai

genai.configure(api_key="AIzaSyCKCcoI_GT1medjXxglgPCxxlgrXomfS1E")

model = genai.GenerativeModel("gemini-2.0-flash")

try:
    result = model.generate_content("Hello")
    print("RESPONSE:", result.text)
except Exception as e:
    print("ERROR:", e)
