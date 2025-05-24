// DOM Elements
const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const appContainer = document.querySelector('.app-container');
let isTyping = false;
let isPaused = false;
let currentSpeech = null;
let jsConfetti = null;
let selectedVoice = null;
let selectedLanguage = 'en-US';

// Initialize MutationObserver for chat box changes
const chatObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    });
});

// Start observing the chat box
chatObserver.observe(chatBox, {
    childList: true,
    subtree: true
});

// Initialize JSConfetti
if (typeof JSConfetti !== 'undefined') {
    jsConfetti = new JSConfetti();
}

// Theme Management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Update theme icon
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    
    // Save preference to localStorage
    localStorage.setItem('theme', newTheme);
}

// Check for saved theme preference
if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = 'fas fa-sun';
}

// Create typing indicator
function createTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("typing-indicator");
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return typingDiv;
}

// Add message to chat
function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    
    const contentContainer = document.createElement("div");
    contentContainer.classList.add("message-content");
    contentContainer.innerHTML = formatMessageText(text);
    
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const timeSpan = document.createElement("span");
    timeSpan.classList.add("timestamp");
    timeSpan.textContent = timestamp;
    
    msg.appendChild(contentContainer);
    msg.appendChild(timeSpan);
    
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Trigger confetti for certain messages
    if (sender === 'bot' && (text.toLowerCase().includes('great') || text.toLowerCase().includes('awesome'))) {
        triggerConfetti();
    }
}

// Format message text (bolden **text**, handle links, etc.)
function formatMessageText(text) {
    // Simple markdown-style bold formatting
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Detect URLs and make them clickable
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Preserve line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

// Quick question buttons
function quickQuestion(question) {
    inputField.value = question;
    sendMessage();
}

// Toggle chat pause
function togglePause() {
    isPaused = !isPaused;
    const pauseButton = document.querySelector('.pause-btn');
    pauseButton.classList.toggle('active');
    
    if (isPaused) {
        pauseButton.innerHTML = '<i class="fas fa-play"></i>';
        inputField.disabled = true;
        inputField.placeholder = "Chat is paused...";
        addMessage("Chat is paused. Click the play button to continue.", "bot");
    } else {
        pauseButton.innerHTML = '<i class="fas fa-pause"></i>';
        inputField.disabled = false;
        inputField.placeholder = "Ask Nova anything...";
        addMessage("Chat resumed. How can I help you?", "bot");
    }
}

// Stop speech synthesis
function stopSpeech() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        currentSpeech = null;
    }
}

// Initialize voice selection
function initializeVoices() {
    const voiceSelect = document.getElementById('voice-select');
    const languageSelect = document.getElementById('language-select');
    
    // Populate voices when they become available
    function populateVoices() {
        const voices = window.speechSynthesis.getVoices();
        voiceSelect.innerHTML = '<option value="">Select Voice</option>';
        
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name} (${voice.lang})`;
            voiceSelect.appendChild(option);
        });
    }
    
    // Initial population
    populateVoices();
    
    // Update voices when they change
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = populateVoices;
    }
    
    // Handle voice selection
    voiceSelect.addEventListener('change', () => {
        selectedVoice = voiceSelect.value;
        if (selectedVoice) {
            const voices = window.speechSynthesis.getVoices();
            const voice = voices.find(v => v.name === selectedVoice);
            if (voice) {
                selectedLanguage = voice.lang;
                languageSelect.value = voice.lang;
            }
        }
    });
    
    // Handle language selection
    languageSelect.addEventListener('change', () => {
        selectedLanguage = languageSelect.value;
        // Update voice selection to match language
        const voices = window.speechSynthesis.getVoices();
        const matchingVoices = voices.filter(v => v.lang.startsWith(selectedLanguage));
        if (matchingVoices.length > 0) {
            voiceSelect.value = matchingVoices[0].name;
            selectedVoice = matchingVoices[0].name;
        }
    });
}

// Modified speakText function to use selected voice and language
function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    
    stopSpeech();
    
    const synth = window.speechSynthesis;
    const utter = new SpeechSynthesisUtterance(text);
    
    // Set voice if selected
    if (selectedVoice) {
        const voices = synth.getVoices();
        const voice = voices.find(v => v.name === selectedVoice);
        if (voice) {
            utter.voice = voice;
        }
    }
    
    // Set language
    utter.lang = selectedLanguage;
    
    // Set other properties
    utter.rate = 1.0;
    utter.pitch = 1.0;
    
    currentSpeech = utter;
    
    utter.onend = () => currentSpeech = null;
    utter.onerror = () => currentSpeech = null;
    
    synth.speak(utter);
}

// Trigger confetti effect
function triggerConfetti() {
    if (jsConfetti) {
        jsConfetti.addConfetti({
            emojis: ['🌈', '⚡️', '💫', '✨', '💥', '🌟'],
            emojiSize: 30,
            confettiNumber: 30,
        });
    }
}

// Send message to backend
async function sendMessage() {
    const message = inputField.value.trim();
    if (!message || isTyping || isPaused) return;

    stopSpeech();
    addMessage(message, "user");
    inputField.value = "";
    isTyping = true;

    const typingIndicator = createTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        
        setTimeout(() => {
            typingIndicator.remove();
            if (!isPaused) {
                addMessage(data.response, "bot");
                speakText(data.response);
            }
            isTyping = false;
        }, 1000);
    } catch (error) {
        typingIndicator.remove();
        addMessage("Sorry, I'm having trouble connecting to my servers. Please try again later.", "bot");
        isTyping = false;
    }
}

// Voice input
function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) {
        addMessage("Voice input isn't supported in your browser", "bot");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    const voiceBtn = document.querySelector('.voice-btn');
    voiceBtn.classList.add('listening');

    recognition.onstart = () => {
        inputField.placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        inputField.value = transcript;
        voiceBtn.classList.remove('listening');
        sendMessage();
    };

    recognition.onerror = (event) => {
        inputField.placeholder = "Ask Nova anything...";
        voiceBtn.classList.remove('listening');
        addMessage("I didn't catch that. Please try again.", "bot");
    };

    recognition.onend = () => {
        inputField.placeholder = "Ask Nova anything...";
        voiceBtn.classList.remove('listening');
    };

    recognition.start();
}

// Event Listeners
inputField.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Initialize with welcome message if empty
if (chatBox.children.length <= 1) {
    setTimeout(() => {
        addMessage("Welcome back! How can I assist you today?", "bot");
    }, 1000);
}

// Initialize voices when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeVoices();
    // ... rest of your initialization code ...
});