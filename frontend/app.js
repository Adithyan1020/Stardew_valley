const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const loadingIndicator = document.getElementById('loadingIndicator');

// The local FastAPI Server URL
const API_URL = "http://127.0.0.1:8000/chat";

// Function to add a message to the UI
function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    
    if (sender === 'user') {
        msgDiv.classList.add('user-message');
    } else {
        msgDiv.classList.add('ai-message');
    }

    // Format newlines into HTML breaks
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    chatBox.appendChild(msgDiv);
    
    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to send message to the backend
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message to UI
    addMessage(text, 'user');
    userInput.value = '';
    
    // Show loading
    loadingIndicator.classList.remove('hidden');
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        // Hide loading and show AI message
        loadingIndicator.classList.add('hidden');
        addMessage(data.answer, 'ai');
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        addMessage("Sorry, I couldn't reach the server. Make sure the FastAPI backend is running!", 'ai');
        console.error("Fetch error:", error);
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
