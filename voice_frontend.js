// Example Frontend Voice Recognition Code with Error Handling

let recognition;
let isListening = false;

// Initialize Speech Recognition
function initVoiceRecognition() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('Speech recognition not supported in this browser');
        alert('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    // Configuration
    recognition.continuous = false;  // Stop after one command
    recognition.interimResults = false;  // Only final results
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    // Event: When speech is recognized
    recognition.onresult = async (event) => {
        const command = event.results[0][0].transcript;
        console.log('Recognized command:', command);
        
        // Show the recognized text to user
        displayMessage(`You said: ${command}`);
        
        // Send to backend
        await sendCommandToServer(command);
    };

    // Event: When speech recognition ends
    recognition.onend = () => {
        console.log('Speech recognition ended');
        isListening = false;
        updateMicButton(false);
    };

    // Event: On error
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        
        let errorMessage = '';
        switch(event.error) {
            case 'no-speech':
                errorMessage = "I didn't hear anything. Please try again.";
                break;
            case 'audio-capture':
                errorMessage = "Microphone not found. Please check your microphone.";
                break;
            case 'not-allowed':
                errorMessage = "Microphone permission denied. Please allow microphone access.";
                break;
            case 'network':
                errorMessage = "Network error. Please check your internet connection.";
                break;
            default:
                errorMessage = `Error: ${event.error}. Please try again.`;
        }
        
        displayMessage(errorMessage, 'error');
        isListening = false;
        updateMicButton(false);
    };

    // Event: When speech starts
    recognition.onstart = () => {
        console.log('Speech recognition started');
        displayMessage('Listening... Speak now!', 'info');
    };
}

// Start listening
function startListening() {
    if (!recognition) {
        initVoiceRecognition();
    }
    
    if (isListening) {
        console.log('Already listening');
        return;
    }
    
    try {
        recognition.start();
        isListening = true;
        updateMicButton(true);
    } catch (error) {
        console.error('Error starting recognition:', error);
        displayMessage('Failed to start listening. Please try again.', 'error');
    }
}

// Stop listening
function stopListening() {
    if (recognition && isListening) {
        recognition.stop();
        isListening = false;
        updateMicButton(false);
    }
}

// Send command to server
async function sendCommandToServer(command) {
    try {
        displayMessage('Processing...', 'info');
        
        const response = await fetch('/voice/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Server response:', data);

        // Handle different action types
        if (data.type === 'redirect') {
            await speakMessage(data.message);
            setTimeout(() => {
                window.location.href = data.url;
            }, 2000);
        } else if (data.type === 'speak') {
            await speakMessage(data.message);
            if (data.stop_listening) {
                stopListening();
            }
        } else if (data.type === 'speak_and_logout') {
            await speakMessage(data.message);
            setTimeout(() => {
                // Add your logout logic here
                window.location.href = '/logout';
            }, 2000);
        }

    } catch (error) {
        console.error('Error sending command:', error);
        displayMessage('Failed to process command. Please try again.', 'error');
    }
}

// Speak message using backend TTS
async function speakMessage(text) {
    try {
        const response = await fetch('/voice/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.audio) {
            // Play the audio
            const audio = new Audio('data:audio/mp3;base64,' + data.audio);
            await audio.play();
            displayMessage(text, 'assistant');
        } else {
            throw new Error('No audio data received');
        }

    } catch (error) {
        console.error('Error playing speech:', error);
        // Fallback: just display the message
        displayMessage(text, 'assistant');
    }
}

// Update microphone button visual state
function updateMicButton(listening) {
    const micButton = document.getElementById('mic-button');
    if (micButton) {
        if (listening) {
            micButton.classList.add('listening');
            micButton.innerHTML = '🎤 Listening...';
        } else {
            micButton.classList.remove('listening');
            micButton.innerHTML = '🎤 Click to Speak';
        }
    }
}

// Display message to user
function displayMessage(message, type = 'info') {
    const messageDiv = document.getElementById('voice-messages');
    if (messageDiv) {
        const p = document.createElement('p');
        p.textContent = message;
        p.className = `voice-message ${type}`;
        messageDiv.appendChild(p);
        
        // Auto-scroll to bottom
        messageDiv.scrollTop = messageDiv.scrollHeight;
        
        // Remove old messages if too many
        while (messageDiv.children.length > 10) {
            messageDiv.removeChild(messageDiv.firstChild);
        }
    } else {
        console.log(message);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initVoiceRecognition();
    
    // Add click handler to mic button
    const micButton = document.getElementById('mic-button');
    if (micButton) {
        micButton.addEventListener('click', function() {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        });
    }
});