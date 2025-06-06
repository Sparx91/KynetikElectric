// Toolie AI Assistant - Chat Widget

class ToolieChat {
    constructor() {
        this.isOpen = false;
        this.context = 'customer-facing'; // or 'solo-operator'
        this.messages = [];
        this.isTyping = false;
        
        this.init();
    }

    init() {
        this.createChatWidget();
        this.bindEvents();
        this.loadWelcomeMessage();
    }

    createChatWidget() {
        // Create chat toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'chat-toggle btn btn-primary';
        toggleButton.innerHTML = '<i class="fas fa-comments"></i>';
        toggleButton.setAttribute('data-bs-toggle', 'tooltip');
        toggleButton.setAttribute('title', 'Chat with Toolie AI');
        document.body.appendChild(toggleButton);

        // Create chat widget
        const chatWidget = document.createElement('div');
        chatWidget.className = 'chat-widget';
        chatWidget.innerHTML = `
            <div class="chat-header">
                <div class="d-flex align-items-center">
                    <i class="fas fa-robot me-2"></i>
                    <span>Toolie AI Assistant</span>
                </div>
                <div class="chat-controls">
                    <select class="form-select form-select-sm me-2" id="chat-context">
                        <option value="customer-facing">Customer Mode</option>
                        <option value="solo-operator">Operator Mode</option>
                    </select>
                    <button class="btn btn-sm btn-outline-light chat-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="chat-messages" id="chat-messages">
                <!-- Messages will be added here -->
            </div>
            <div class="chat-input">
                <input type="text" class="form-control" id="chat-input" placeholder="Ask Toolie anything...">
                <button class="btn btn-primary" id="send-message">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
        document.body.appendChild(chatWidget);

        this.widget = chatWidget;
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-message');
        this.contextSelect = document.getElementById('chat-context');
    }

    bindEvents() {
        // Toggle chat
        document.querySelector('.chat-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.querySelector('.chat-close').addEventListener('click', () => {
            this.closeChat();
        });

        // Send message
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Context change
        this.contextSelect.addEventListener('change', (e) => {
            this.context = e.target.value;
            this.addSystemMessage(`Switched to ${e.target.value.replace('-', ' ')} mode`);
        });

        // Auto-resize input
        this.inputField.addEventListener('input', () => {
            this.inputField.style.height = 'auto';
            this.inputField.style.height = this.inputField.scrollHeight + 'px';
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.widget.style.display = 'block';
        this.isOpen = true;
        this.inputField.focus();
        
        // Animate in
        setTimeout(() => {
            this.widget.style.opacity = '1';
            this.widget.style.transform = 'translateY(0)';
        }, 10);
    }

    closeChat() {
        this.widget.style.opacity = '0';
        this.widget.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            this.widget.style.display = 'none';
            this.isOpen = false;
        }, 300);
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message || this.isTyping) return;

        // Add user message
        this.addMessage(message, 'user');
        this.inputField.value = '';
        this.inputField.style.height = 'auto';

        // Show typing indicator
        this.showTyping();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: this.context
                })
            });

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            // Add bot response
            this.addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addMessage('Sorry, I\'m experiencing technical difficulties. Please try again later.', 'bot');
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        if (sender === 'bot') {
            messageDiv.innerHTML = `
                <div class="d-flex align-items-start">
                    <i class="fas fa-robot me-2 mt-1"></i>
                    <div>${this.formatMessage(content)}</div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="d-flex align-items-start justify-content-end">
                    <div>${this.formatMessage(content)}</div>
                    <i class="fas fa-user ms-2 mt-1"></i>
                </div>
            `;
        }

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message
        this.messages.push({ content, sender, timestamp: new Date() });
    }

    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message system text-center';
        messageDiv.innerHTML = `<small class="text-muted"><i>${content}</i></small>`;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="fas fa-robot me-2 mt-1"></i>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        // Add typing animation CSS if not already present
        if (!document.getElementById('typing-styles')) {
            const style = document.createElement('style');
            style.id = 'typing-styles';
            style.textContent = `
                .typing-dots {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }
                .typing-dots span {
                    width: 6px;
                    height: 6px;
                    background: var(--primary-blue);
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }
                .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                @keyframes typing {
                    0%, 80%, 100% {
                        transform: scale(0.8);
                        opacity: 0.5;
                    }
                    40% {
                        transform: scale(1);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    formatMessage(content) {
        // Convert line breaks to <br>
        content = content.replace(/\n/g, '<br>');
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert **text** to bold
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *text* to italic
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        return content;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    loadWelcomeMessage() {
        setTimeout(() => {
            const welcomeMessage = this.context === 'customer-facing' 
                ? "Hi! I'm Toolie, your AI assistant for Kynetik Electric. I can help you understand our services, guide you through bid requests, and answer electrical questions. How can I help you today?"
                : "Hello! I'm Toolie in operator mode. I can assist with technical calculations, code references, troubleshooting guidance, and project planning. What do you need help with?";
            
            this.addMessage(welcomeMessage, 'bot');
        }, 500);
    }

    // Quick actions for common requests
    addQuickActions() {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'quick-actions p-2';
        
        const actions = this.context === 'customer-facing' 
            ? ['Request a Bid', 'View Services', 'Get Quote Estimate', 'Emergency Contact']
            : ['Calculate Load', 'Check Code', 'Troubleshoot Issue', 'Generate Quote'];
        
        actionsDiv.innerHTML = actions.map(action => 
            `<button class="btn btn-sm btn-outline-primary m-1" onclick="toolieChat.sendQuickAction('${action}')">${action}</button>`
        ).join('');
        
        this.messagesContainer.appendChild(actionsDiv);
        this.scrollToBottom();
    }

    sendQuickAction(action) {
        this.inputField.value = action;
        this.sendMessage();
    }
}

// Initialize Toolie Chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.toolieChat = new ToolieChat();
    
    // Add context-aware suggestions based on current page
    const currentPage = window.location.pathname;
    if (currentPage.includes('bid-request')) {
        setTimeout(() => {
            toolieChat.addMessage("I see you're on the bid request page. I can help you fill out the form or answer any questions about our services!", 'bot');
        }, 2000);
    } else if (currentPage.includes('quote-estimator')) {
        setTimeout(() => {
            toolieChat.addMessage("Need help with the quote estimator? I can explain how different factors affect pricing or help you get a more accurate estimate.", 'bot');
        }, 2000);
    } else if (currentPage.includes('troubleshooting')) {
        setTimeout(() => {
            toolieChat.addMessage("I can help diagnose electrical issues and provide safety guidance. Describe what you're experiencing and I'll guide you through the next steps.", 'bot');
        }, 2000);
    }
});

// Export for use in other scripts
window.ToolieChat = ToolieChat;
