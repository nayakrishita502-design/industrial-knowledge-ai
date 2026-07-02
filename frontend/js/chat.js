// Chat Module

const chatBox = document.getElementById('chatBox');
const queryInput = document.getElementById('queryInput');
const askBtn = document.getElementById('askBtn');
const clearChatBtn = document.getElementById('clearChatBtn');

// Event listeners
askBtn.addEventListener('click', askQuestion);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});

clearChatBtn.addEventListener('click', clearChat);

// Handle suggestion buttons
document.querySelectorAll('.suggestion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        queryInput.value = btn.textContent.trim();
        askQuestion();
    });
});

async function askQuestion() {
    const question = queryInput.value.trim();
    
    if (!question) return;
    
    // Remove welcome message if present
    const welcomeMsg = chatBox.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message
    addMessage(question, 'user');
    queryInput.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        const data = await apiRequest('/queries/ask', {
            method: 'POST',
            body: JSON.stringify({ 
                question,
                num_sources: 4
            })
        });
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.error) {
            addMessage(`Error: ${data.error}`, 'bot', true);
        } else {
            addMessage(data.answer, 'bot', false, data.sources);
        }
        
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage(`Error: ${error.message}`, 'bot', true);
    }
}

function addMessage(content, sender, isError = false, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    let messageContent = `
        <div class="message-content ${isError ? 'bg-danger text-white' : ''}">
            ${sender === 'bot' ? formatResponse(content) : escapeHtml(content)}
        </div>
    `;
    
    // Add sources if available
    if (sources && sources.length > 0) {
        messageContent += `
            <div class="message-sources mt-2">
                <small class="text-muted fw-bold">
                    <i class="bi bi-journal-text me-1"></i>Sources (${sources.length}):
                </small>
                ${sources.map((source, i) => `
                    <div class="source-item">
                        <small class="text-muted">
                            <strong>${i + 1}.</strong> ${escapeHtml(source.content || source)}
                        </small>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = messageContent;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'chat-message bot-message';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

function clearChat() {
    chatBox.innerHTML = `
        <div class="welcome-message text-center py-5">
            <i class="bi bi-chat-dots display-4 text-muted"></i>
            <p class="text-muted mt-3">
                Upload documents and ask questions about maintenance, 
                procedures, equipment, or safety protocols.
            </p>
            <div class="suggested-questions mt-3">
                <p class="small text-muted mb-2">Try asking:</p>
                <button class="btn btn-outline-secondary btn-sm m-1 suggestion-btn">
                    What maintenance procedures are documented?
                </button>
                <button class="btn btn-outline-secondary btn-sm m-1 suggestion-btn">
                    What equipment failures have occurred?
                </button>
                <button class="btn btn-outline-secondary btn-sm m-1 suggestion-btn">
                    What safety hazards are identified?
                </button>
            </div>
        </div>
    `;
    
    // Re-attach event listeners to new suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            queryInput.value = btn.textContent.trim();
            askQuestion();
        });
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}