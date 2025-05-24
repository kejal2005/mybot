import os
import requests
import google.generativeai as genai
import time
from custom_aiml import CustomAIMLKernel
from config import GEMINI_API_KEY  # Import from config instead of .env

# Configure the API with explicit settings
genai.configure(
    api_key=GEMINI_API_KEY,
    transport='rest'  # Use REST transport explicitly
)

# Initialize Gemini model
try:
    model = genai.GenerativeModel(
        model_name='gemini-pro',
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40
        }
    )
    # Test the model
    test_response = model.generate_content("Hello")
    if not test_response or not test_response.text:
        raise ValueError("Model initialization test failed")
except Exception as e:
    print(f"Error initializing Gemini model: {str(e)}")
    model = None

def initialize_bot():
    try:
        kernel = CustomAIMLKernel()
        aiml_path = "aiml"
        
        if not os.path.exists(aiml_path):
            print(f"Folder '{aiml_path}' not found! Create it and place your AIML files inside.")
            return None
            
        for file in os.listdir(aiml_path):
            if file.endswith(".aiml"):
                try:
                    print(f"Loading {file}...")
                    kernel.learn(os.path.join(aiml_path, file))
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
        
        return kernel
    except Exception as e:
        print(f"Error initializing bot: {str(e)}")
        return None

def main():
    print(">> Initializing ChatBot...")
    kernel = initialize_bot()
    
    if kernel is None:
        print("Failed to initialize ChatBot. Please check the AIML files.")
        return
    
    print("🤖 ChatBot is ready! Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                print("Goodbye!")
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
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()