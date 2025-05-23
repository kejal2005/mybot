from flask import Flask, request, jsonify, render_template, send_from_directory
import aiml
import os
import requests
from flask_cors import CORS
import google.generativeai as genai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app with static folder configuration
app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static',
    template_folder='templates'
)
CORS(app)

# Initialize AIML kernel
kernel = None

def initialize_aiml():
    global kernel
    if kernel is None:
        kernel = CustomKernel()
        aiml_path = "aiml"
        
        if not os.path.exists(aiml_path):
            print(f"Folder '{aiml_path}' not found!")
            return False
            
        for file in os.listdir(aiml_path):
            if file.endswith(".aiml"):
                try:
                    kernel.learn(os.path.join(aiml_path, file))
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
        return True
    return True

class CustomKernel(aiml.Kernel):
    def learn(self, file_name):
        start = time.perf_counter()
        super().learn(file_name)
        end = time.perf_counter()
        print(f"Time taken to learn {file_name}: {end - start:.2f} seconds")

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory('static', path)

@app.route("/chat", methods=["POST"])
def chat():
    if not initialize_aiml():
        return jsonify({"response": "Error: AIML system not properly initialized."})

    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "No input received."})

    try:
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
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"response": "I'm having trouble processing your request. Please try again."})

def get_joke():
    try:
        joke = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return f"{joke['setup']} ... {joke['punchline']}"
    except Exception as e:
        print(f"Joke API Error: {str(e)}")
        return "Sorry, I couldn't fetch a joke right now. 😅"

def get_news():
    try:
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
    # Run the app on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)