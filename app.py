from flask import Flask, request, jsonify, render_template
import aiml
import os
import requests
from flask_cors import CORS
import google.generativeai as genai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# List available models to verify
try:
    models = [m.name for m in genai.list_models()]
    print("Available models:", models)
    model = genai.GenerativeModel(model_name='models/gemini-1.5-pro', generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.7
    })
except Exception as e:
    print(f"Error initializing Gemini model: {str(e)}")
    model = None

class CustomKernel(aiml.Kernel):
    def learn(self, file_name):
        start = time.perf_counter()
        super().learn(file_name)
        end = time.perf_counter()
        print(f"Time taken to learn {file_name}: {end - start:.2f} seconds")

kernel = CustomKernel()
aiml_path = "aiml"

if not os.path.exists(aiml_path):
    print(f"Folder '{aiml_path}' not found! Create it and place your AIML files inside.")
    exit()

for file in os.listdir(aiml_path):
    if file.endswith(".aiml"):
        try:
            kernel.learn(os.path.join(aiml_path, file))
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "No input received."})

    response = kernel.respond(user_input)
    topic = kernel.getPredicate("topic")

    if topic == "joke":
        response = get_joke()
    elif topic == "weather":
        response = "Weather APIs need a location. Try asking: 'What's the weather in Delhi?'"
    elif topic == "news":
        response = get_news()
    elif topic == "gemini" or not response or response.lower() in ["i don't know", "i'm not sure how to respond to that yet. try asking me something else!", ""]:
        response = get_gemini_response(user_input)

    kernel.setPredicate("topic", "")
    return jsonify({"response": response})

def get_joke():
    try:
        joke = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return f"{joke['setup']} ... {joke['punchline']}"
    except Exception as e:
        print(f"Joke API Error: {str(e)}")
        return "Sorry, I couldn't fetch a joke right now. 😅"

def get_news():
    try:
        # Replace with your actual news API key
        return "News API functionality needs to be configured with a valid API key"
    except Exception as e:
        print(f"News API Error: {str(e)}")
        return "Something went wrong while fetching the news. 😓"

def get_gemini_response(user_input):
    try:
        if model is None:
            return "Gemini API is not properly configured. Please check your API key and try again."
            
        response = model.generate_content(user_input)
        if response.text:
            return response.text
        return "I couldn't generate a response. Please try again."
    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        return "I'm having trouble connecting to my knowledge base. Please try again later."

if __name__ == "__main__":
    app.run(debug=True, port=5000)