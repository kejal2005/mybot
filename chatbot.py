import aiml
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

kernel = aiml.Kernel()
aiml_path = "aiml"

if not os.path.exists(aiml_path):
    print(f"Folder '{aiml_path}' not found! Please create it and add AIML files.")
    exit()

for file in os.listdir(aiml_path):
    if file.endswith(".aiml"):
        try:
            kernel.learn(os.path.join(aiml_path, file))
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

print("🤖 ChatBot is ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        print("ChatBot: Goodbye! 👋")
        break

    response = kernel.respond(user_input)
    topic = kernel.getPredicate("topic")

    if not response or response.lower() in ["i don't know", "i'm not sure how to respond to that yet. try asking me something else!", ""]:
        try:
            response = model.generate_content(
                user_input,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.7
                }
            ).text
        except Exception as e:
            print(f"Gemini Error: {str(e)}")
            response = "I'm having trouble connecting to my knowledge base. Please try again later."

    elif topic == "joke":
        try:
            joke = requests.get("https://official-joke-api.appspot.com/random_joke").json()
            response = f"{joke['setup']} ... {joke['punchline']}"
        except Exception as e:
            print(f"Joke API Error: {str(e)}")
            response = "Sorry, I couldn't fetch a joke right now. 😅"
        kernel.setPredicate("topic", "")

    elif topic == "weather":
        response = "Weather APIs need a location. Try asking: 'What's the weather in Delhi?'"
        kernel.setPredicate("topic", "")

    elif topic == "gemini":
        try:
            response = model.generate_content(
                user_input,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.7
                }
            ).text
        except Exception as e:
            print(f"Gemini Error: {str(e)}")
            response = "I'm having trouble connecting to my knowledge base. Please try again later."
        kernel.setPredicate("topic", "")

    print(f"ChatBot: {response}")