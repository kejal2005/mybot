# AI Chatbot

An intelligent chatbot built using Python, AIML, and Google's Gemini AI. This chatbot combines rule-based responses with advanced AI capabilities to provide natural and helpful conversations.

## Features

- Rule-based responses using AIML
- Integration with Google's Gemini AI for advanced conversations
- Web interface for easy interaction
- Support for various topics including:
  - General conversation
  - Jokes
  - News
  - Weather
  - General knowledge queries

## Project Structure

```
├── aiml/              # AIML files for rule-based responses
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
├── app.py           # Main Flask application
├── chatbot.py       # Chatbot core logic
├── custom_aiml.py   # Custom AIML implementation
├── test_gemini.py   # Gemini AI integration tests
└── requirements.txt # Project dependencies
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatbot.git
cd chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Start chatting with the bot!

## Technologies Used

- Python
- Flask
- AIML
- Google Gemini AI
- HTML/CSS/JavaScript

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Google Gemini API Key
GEMINI_API_KEY=your_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py 