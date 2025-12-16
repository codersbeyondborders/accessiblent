(function() {
    'use strict';
    
    const API = window.ACCESSIFY_API_BASE || 'http://localhost:8000';
    const PAGE_ID = window.ACCESSIFY_PAGE_ID;
    const MAX_QUESTIONS = 3;
    
    let state = {
        fontSize: 100,
        highContrast: false,
        grayscale: false,
        letterSpacing: 0,
        isMinimized: false,
        showChat: false,
        chat: [],
        chatQuestion: '',
        isThinking: false,
        questionCount: 0
    };
    
    // Load saved preferences
    function loadPreferences() {
        const saved = localStorage.getItem('a11y-preferences');
        if (saved) {
            try {
                const prefs = JSON.parse(saved);
                state.fontSize = prefs.fontSize || 100;
                state.highContrast = prefs.highContrast || false;
                state.grayscale = prefs.grayscale || false;
                state.letterSpacing = prefs.letterSpacing || 0;
            } catch (e) {
                console.error('Failed to load preferences:', e);
            }
        }
    }
    
    // Save preferences
    function savePreferences() {
        localStorage.setItem('a11y-preferences', JSON.stringify({
            fontSize: state.fontSize,
            highContrast: state.highContrast,
            grayscale: state.grayscale,
            letterSpacing: state.letterSpacing
        }));
    }
    
    // Apply settings
    function applySettings() {
        const root = document.documentElement;
        root.style.fontSize = state.fontSize + '%';
        root.style.letterSpacing = state.letterSpacing + 'px';
        
        if (state.highContrast) {
            root.classList.add('high-contrast');
        } else {
            root.classList.remove('high-contrast');
        }
        
        if (state.grayscale) {
            root.classList.add('grayscale');
        } else {
            root.classList.remove('grayscale');
        }
        
        savePreferences();
    }
    
    // Font size controls
    function increaseFontSize() {
        state.fontSize = Math.min(state.fontSize + 10, 150);
        applySettings();
        updateToolbar();
    }
    
    function decreaseFontSize() {
        state.fontSize = Math.max(state.fontSize - 10, 80);
        applySettings();
        updateToolbar();
    }
    
    // Contrast toggle
    function toggleContrast() {
        state.highContrast = !state.highContrast;
        applySettings();
        updateToolbar();
    }
    
    // Grayscale toggle
    function toggleGrayscale() {
        state.grayscale = !state.grayscale;
        applySettings();
        updateToolbar();
    }
    
    // Letter spacing controls
    function increaseSpacing() {
        state.letterSpacing = Math.min(state.letterSpacing + 1, 5);
        applySettings();
        updateToolbar();
    }
    
    function decreaseSpacing() {
        state.letterSpacing = Math.max(state.letterSpacing - 1, 0);
        applySettings();
        updateToolbar();
    }
    
    // Reset all
    function resetAll() {
        state.fontSize = 100;
        state.highContrast = false;
        state.grayscale = false;
        state.letterSpacing = 0;
        applySettings();
        updateToolbar();
    }
    
    // Toggle minimize
    function toggleMinimize() {
        state.isMinimized = !state.isMinimized;
        updateToolbar();
    }
    
    // Chat functions
    function toggleChat() {
        state.showChat = !state.showChat;
        if (state.showChat) {
            state.chatQuestion = '';
        }
        updateToolbar();
    }
    
    async function sendMessage() {
        const question = state.chatQuestion.trim();
        if (!question || state.questionCount >= MAX_QUESTIONS || state.isThinking) return;
        
        // Add user message
        state.chat.push({ role: 'user', text: question, ts: Date.now() });
        state.chatQuestion = '';
        state.questionCount++;
        state.isThinking = true;
        updateToolbar();
        
        try {
            const res = await fetch(`${API}/chat/${PAGE_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ question })
            });
            
            if (!res.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await res.json();
            const answer = data.answer || 'Sorry, I could not generate a response.';
            state.chat.push({ role: 'assistant', text: answer, ts: Date.now() });
        } catch (err) {
            state.chat.push({ 
                role: 'assistant', 
                text: 'Sorry, there was an error processing your question.', 
                ts: Date.now() 
            });
        } finally {
            state.isThinking = false;
            updateToolbar();
        }
    }
    
    // Create toolbar HTML
    function createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'accessify-toolbar';
        toolbar.id = 'accessify-toolbar';
        document.body.appendChild(toolbar);
        updateToolbar();
    }
    
    // Update toolbar HTML
    function updateToolbar() {
        const toolbar = document.getElementById('accessify-toolbar');
        if (!toolbar) return;
        
        toolbar.className = 'accessify-toolbar' + (state.isMinimized ? ' minimized' : '');
        
        toolbar.innerHTML = `
            <div class="accessify-toolbar-container">
                <div class="accessify-toolbar-content">
                    <button class="accessify-toolbar-toggle ${state.isMinimized ? 'minimized' : ''}" 
                            onclick="window.accessifyToolbar.toggleMinimize()"
                            aria-label="${state.isMinimized ? 'Show' : 'Hide'} accessibility toolbar">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>
                    
                    <div class="accessify-toolbar-controls">
                        <div class="accessify-control-group">
                            <span class="accessify-control-label">Font Size</span>
                            <button class="accessify-btn" onclick="window.accessifyToolbar.decreaseFontSize()" aria-label="Decrease font size">A-</button>
                            <span class="accessify-value">${state.fontSize}%</span>
                            <button class="accessify-btn" onclick="window.accessifyToolbar.increaseFontSize()" aria-label="Increase font size">A+</button>
                        </div>
                        
                        <button class="accessify-btn ${state.highContrast ? 'active' : ''}" 
                                onclick="window.accessifyToolbar.toggleContrast()"
                                aria-pressed="${state.highContrast}">
                            Contrast
                        </button>
                        
                        <button class="accessify-btn ${state.grayscale ? 'active' : ''}" 
                                onclick="window.accessifyToolbar.toggleGrayscale()"
                                aria-pressed="${state.grayscale}">
                            Grayscale
                        </button>
                        
                        <div class="accessify-control-group">
                            <span class="accessify-control-label">Spacing</span>
                            <button class="accessify-btn" onclick="window.accessifyToolbar.decreaseSpacing()" aria-label="Decrease letter spacing">-</button>
                            <span class="accessify-value">${state.letterSpacing}px</span>
                            <button class="accessify-btn" onclick="window.accessifyToolbar.increaseSpacing()" aria-label="Increase letter spacing">+</button>
                        </div>
                        
                        <button class="accessify-btn-primary" onclick="window.accessifyToolbar.toggleChat()">
                            <svg style="width: 1rem; height: 1rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            Ask AI
                        </button>
                        
                        <button class="accessify-btn-reset" onclick="window.accessifyToolbar.resetAll()" aria-label="Reset all settings">Reset</button>
                    </div>
                </div>
            </div>
        `;
        
        // Update chat modal
        updateChatModal();
    }
    
    // Update chat modal
    function updateChatModal() {
        let modal = document.getElementById('accessify-chat-modal');
        
        if (!state.showChat) {
            if (modal) modal.remove();
            return;
        }
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'accessify-chat-modal';
            modal.className = 'accessify-chat-modal';
            document.body.appendChild(modal);
        }
        
        const remaining = Math.max(0, MAX_QUESTIONS - state.questionCount);
        
        modal.innerHTML = `
            <div class="accessify-chat-container">
                <div class="accessify-chat-header">
                    <div>
                        <div class="accessify-chat-title">Chat with AI Assistant</div>
                        <div class="accessify-chat-subtitle">Questions left: ${remaining}</div>
                    </div>
                    <button class="accessify-chat-close" onclick="window.accessifyToolbar.toggleChat()" aria-label="Close chat">
                        <svg style="width: 1.5rem; height: 1.5rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div class="accessify-chat-messages" id="accessify-chat-messages">
                    ${state.chat.length === 0 ? '<div class="accessify-chat-empty">Ask questions about the accessibility improvements and content on this page.</div>' : ''}
                    ${state.chat.map(msg => `
                        <div class="accessify-chat-message ${msg.role}">
                            <div class="accessify-chat-bubble ${msg.role}">${escapeHtml(msg.text)}</div>
                        </div>
                    `).join('')}
                    ${state.isThinking ? '<div class="accessify-chat-thinking"><div class="accessify-spinner"></div><span style="font-size: 0.875rem; color: #6b7280;">Thinking...</span></div>' : ''}
                </div>
                
                <div class="accessify-chat-input-area">
                    ${state.questionCount >= MAX_QUESTIONS ? `
                        <div class="accessify-chat-limit-warning">
                            You've reached the limit of ${MAX_QUESTIONS} questions. Refresh the page to start over.
                        </div>
                    ` : ''}
                    <div class="accessify-chat-input-wrapper">
                        <textarea 
                            class="accessify-chat-textarea" 
                            id="accessify-chat-input"
                            placeholder="Ask about accessibility improvements..."
                            ${state.isThinking || state.questionCount >= MAX_QUESTIONS ? 'disabled' : ''}
                            aria-label="Chat message"
                        >${state.chatQuestion}</textarea>
                        <button 
                            class="accessify-chat-send" 
                            onclick="window.accessifyToolbar.sendMessage()"
                            ${state.isThinking || state.questionCount >= MAX_QUESTIONS ? 'disabled' : ''}>
                            ${state.isThinking ? '<div class="accessify-spinner"></div>' : 'Send'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Attach input handler
        const input = document.getElementById('accessify-chat-input');
        if (input) {
            input.addEventListener('input', (e) => {
                state.chatQuestion = e.target.value;
            });
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            input.focus();
        }
        
        // Scroll to bottom
        const messages = document.getElementById('accessify-chat-messages');
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Initialize
    function init() {
        loadPreferences();
        applySettings();
        createToolbar();
        
        // Add padding to body to prevent toolbar from covering content
        document.body.style.paddingBottom = '4rem';
    }
    
    // Expose API
    window.accessifyToolbar = {
        increaseFontSize,
        decreaseFontSize,
        toggleContrast,
        toggleGrayscale,
        increaseSpacing,
        decreaseSpacing,
        resetAll,
        toggleMinimize,
        toggleChat,
        sendMessage
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
