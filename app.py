from flask import Flask, request, jsonify, render_template, send_from_directory
import aiml
import os
import requests
from flask_cors import CORS
import google.generativeai as genai
import time
from config import GEMINI_API_KEY  # Import directly from config

# Initialize Flask app with static folder configuration
app = Flask(__name__, 
    static_folder='static',
    static_url_path='',
    template_folder='templates'
)
CORS(app)

# Initialize AIML kernel
kernel = None

# Debug logging for API key
print("\n=== API Key Configuration ===")
print(f"API Key loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
print(f"API Key length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")
print(f"API Key prefix: {GEMINI_API_KEY[:5] if GEMINI_API_KEY else 'None'}...")
print("===========================\n")

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
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set in config.py")
    raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY in config.py")

if not GEMINI_API_KEY.startswith("AI"):
    print("Error: Invalid GEMINI_API_KEY format")
    raise ValueError("Invalid Gemini API key format. API key should start with 'AI'.")

print("Initializing Gemini API...")
print(f"API Key length: {len(GEMINI_API_KEY)}")
print(f"API Key prefix: {GEMINI_API_KEY[:5]}...")

# Configure the API with minimal settings
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Successfully configured Gemini API")
    
    # Test the API key with a simple request
    print("Testing API key with a simple request...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content("Say hello")
    if response and response.text:
        print("API key test successful!")
        print(f"Test response: {response.text}")
    else:
        raise ValueError("API key test failed - no response received")
        
except Exception as e:
    print(f"Error during API key test: {str(e)}")
    print(f"Error type: {type(e)}")
    if "API key" in str(e).lower():
        print("API key validation failed. Please check your Gemini API key.")
    elif "quota" in str(e).lower():
        print("API quota exceeded. Please check your usage limits.")
    elif "429" in str(e):
        print("Rate limit exceeded. Please try again later.")
    raise

# Initialize Gemini model
try:
    print("Fetching available models...")
    models = [m.name for m in genai.list_models()]
    print("Available models:", models)
    
    # Try to use gemini-1.5-pro-latest first, fall back to gemini-1.0-pro if needed
    try:
        print("Initializing gemini-1.5-pro-latest model...")
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("Successfully initialized gemini-1.5-pro-latest model")
    except Exception as e:
        print(f"Failed to initialize gemini-1.5-pro-latest, trying gemini-1.0-pro: {str(e)}")
        model = genai.GenerativeModel('gemini-1.0-pro')
        print("Successfully initialized gemini-1.0-pro model")
    
    # Test the model with a simple prompt
    print("Testing model with simple prompt...")
    test_response = model.generate_content("Hello")
    if test_response and test_response.text:
        print("Model test successful!")
    else:
        raise ValueError("Model test failed - no response received")
        
except Exception as e:
    print(f"Error initializing Gemini model: {str(e)}")
    print(f"Error type: {type(e)}")
    print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
    if "API key" in str(e).lower():
        print("API key validation failed. Please check your Gemini API key.")
    elif "quota" in str(e).lower():
        print("API quota exceeded. Please check your usage limits.")
    elif "429" in str(e):
        print("Rate limit exceeded. Please try again later.")
    model = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory('static', path)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not initialize_aiml():
            print("AIML initialization failed")
            return jsonify({"response": "Error: AIML system not properly initialized."})

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
            print("Gemini model is not initialized")
            return "Gemini API is not properly configured. Please check your API key and try again."
            
        print(f"Generating response for: {user_input[:50]}...")
        response = model.generate_content(user_input)
        
        if response and response.text:
            print("Response generated successfully")
            return response.text
            
        print("No response text received")
        return "I couldn't generate a response. Please try again."
        
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini Error: {error_msg}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
        
        if "API key" in error_msg.lower():
            return "API key error: Please check your Gemini API key configuration."
        elif "quota" in error_msg.lower():
            return "API quota exceeded: Please check your Gemini API usage limits."
        elif "timeout" in error_msg.lower():
            return "Request timeout: Please try again in a few moments."
        else:
            return f"Error: {error_msg}. Please try again later."

# For local development
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)