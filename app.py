from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

# ==========================================
# HTML TEMPLATE (Frontend)
# ==========================================
HTML_TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Raze AI</title>
    <!-- Ionicons for UI Icons -->
    <script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        /* CSS VARIABLES & THEMES */
        :root {
            --transition-speed: 0.2s;
            --font-main: 'Inter', sans-serif;
            --font-code: 'JetBrains Mono', monospace;
        }

        [data-theme="dark"] {
            --background: #0C0C0C;
            --surface: #161616;
            --surface-elevated: #1E1E1E;
            --text: #FFFFFF;
            --text-secondary: #A1A1A1;
            --text-tertiary: #6B7280;
            --user-bubble: #2563EB;
            --ai-bubble: #1A1A1A;
            --border: #262626;
            --border-light: #1A1A1A;
            --code-background: #0A0A0A;
            --code-header: #1A1A1A;
            --code-text: #22C55E;
            --overlay: rgba(0, 0, 0, 0.6);
            --shadow: rgba(0, 0, 0, 0.3);
            --sidebar-bg: #121212;
            --sidebar-surface: #1A1A1A;
            --highlight: #FFD700;
            --bold-text: #FFFFFF;
            --new-chat-bg: #FFFFFF;
            --new-chat-text: #000000;
            --scrollbar-thumb: #333;
        }

        [data-theme="light"] {
            --background: #FFFFFF;
            --surface: #F8FAFC;
            --surface-elevated: #FFFFFF;
            --text: #0F172A;
            --text-secondary: #64748B;
            --text-tertiary: #94A3B8;
            --user-bubble: #2563EB;
            --ai-bubble: #F1F5F9;
            --border: #E2E8F0;
            --border-light: #F1F5F9;
            --code-background: #F8FAFC;
            --code-header: #E2E8F0;
            --code-text: #059669;
            --overlay: rgba(0, 0, 0, 0.4);
            --shadow: rgba(0, 0, 0, 0.1);
            --sidebar-bg: #FAFAFA;
            --sidebar-surface: #FFFFFF;
            --highlight: #FF6B35;
            --bold-text: #1F2937;
            --new-chat-bg: #000000;
            --new-chat-text: #FFFFFF;
            --scrollbar-thumb: #CCC;
        }

        /* RESET & BASE */
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; font-family: var(--font-main); background-color: var(--background); color: var(--text); overflow: hidden; }

        /* LAYOUT */
        #app { display: flex; flex-direction: column; height: 100vh; height: 100dvh; position: relative; transition: background-color var(--transition-speed); }

        /* HEADER */
        .header {
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 0.5px solid var(--border-light);
            background: var(--background);
            z-index: 100;
            padding-top: max(10px, env(safe-area-inset-top));
            flex-shrink: 0;
        }

        .app-title { font-size: 20px; font-weight: 700; color: var(--text); letter-spacing: -0.3px; }

        .icon-btn {
            width: 44px; height: 44px; border-radius: 12px; border: none; background: var(--surface);
            display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-secondary);
            transition: transform 0.1s;
            z-index: 10;
        }
        .icon-btn:active { transform: scale(0.95); }
        .icon-btn ion-icon { font-size: 22px; pointer-events: none; }

        /* CHAT AREA */
        .chat-container {
            flex: 1; 
            overflow-y: auto; 
            padding: 20px; 
            display: flex; 
            flex-direction: column; 
            min-height: 0; 
            scroll-behavior: smooth;
        }
        .chat-container::-webkit-scrollbar { width: 6px; }
        .chat-container::-webkit-scrollbar-thumb { background: transparent; border-radius: 3px; }
        .chat-container:hover::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); }

        .message-row { display: flex; margin-bottom: 16px; width: 100%; }
        .message-row.user { justify-content: flex-end; }
        .message-row.ai { justify-content: flex-start; }

        .message-bubble {
            max-width: 85%; display: flex; align-items: flex-start; position: relative;
        }
        .message-row.user .message-bubble { flex-direction: row-reverse; }
        
        .ai-avatar {
            width: 32px; height: 32px; border-radius: 8px; background: var(--surface-elevated);
            border: 1px solid var(--border); margin-right: 12px; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }

        .message-content {
            background: var(--ai-bubble); padding: 14px 18px; border-radius: 20px;
            color: var(--text); font-size: 16px; line-height: 24px; letter-spacing: -0.1px;
            overflow-wrap: break-word; max-width: 100%;
        }
        .message-row.user .message-content { background: var(--user-bubble); color: #fff; border-bottom-right-radius: 4px; }
        .message-row.ai .message-content { border-bottom-left-radius: 4px; }

        /* Markdown Styles */
        .md-bold { font-weight: 700; }
        .md-header { font-weight: 700; margin: 8px 0; display: block; }
        .md-h1 { font-size: 20px; color: var(--highlight); }
        .md-h2 { font-size: 18px; color: var(--highlight); }
        .md-h3 { font-size: 16px; color: var(--highlight); }
        
        .code-block {
            background: var(--code-background); border: 1px solid var(--border);
            border-radius: 12px; margin: 8px 0; overflow: hidden;
        }
        .code-header {
            background: var(--code-header); border-bottom: 1px solid var(--border);
            padding: 8px 16px; display: flex; justify-content: space-between; align-items: center;
        }
        .code-lang { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.5px; }
        .copy-btn {
            background: transparent; border: none; color: var(--text-secondary);
            font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 4px;
        }
        .copy-btn:hover { color: var(--user-bubble); }
        .code-content {
            padding: 16px; font-family: var(--font-code); font-size: 14px; color: var(--code-text);
            overflow-x: auto; white-space: pre; line-height: 1.4;
        }

        /* Empty State */
        .empty-state {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            flex: 1; text-align: center; padding: 20px; width: 100%;
        }
        .empty-avatar {
            width: 80px; height: 80px; border-radius: 20px; background: linear-gradient(135deg, #2563EB, #60A5FA);
            display: flex; align-items: center; justify-content: center; margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        .empty-title { font-size: 28px; font-weight: 700; margin-bottom: 12px; color: var(--text); }
        .empty-subtitle { font-size: 16px; color: var(--text-secondary); line-height: 24px; max-width: 400px; }

        /* INPUT AREA */
        .input-area-container {
            background: var(--background); border-top: 0.5px solid var(--border-light);
            padding: 20px; position: relative; padding-bottom: max(20px, env(safe-area-inset-bottom));
            flex-shrink: 0;
        }
        .input-wrapper {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 20px; display: flex; align-items: flex-end; padding: 12px 18px;
            box-shadow: 0 2px 8px var(--shadow);
            position: relative;
        }
        #chat-input {
            flex: 1; background: transparent; border: none; color: var(--text);
            font-size: 16px; font-family: var(--font-main); resize: none; outline: none;
            max-height: 120px; min-height: 24px; padding: 8px 0; margin-right: 12px;
        }
        #chat-input::placeholder { color: var(--text-tertiary); }
        
        .send-btn {
            width: 40px; height: 40px; border-radius: 20px; border: none;
            background: var(--user-bubble); color: #fff; display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: transform 0.1s, opacity 0.2s, box-shadow 0.2s;
            z-index: 5;
            padding: 0;
            opacity: 0.5;
        }
        
        .send-btn.active-glow {
            opacity: 1;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.6);
            transform: scale(1.05);
        }

        .send-btn:active { transform: scale(0.9); }
        .send-btn:disabled { 
            opacity: 0.3; 
            cursor: not-allowed; 
            pointer-events: none; 
            box-shadow: none;
            transform: scale(1);
        }
        
        .icon-wrapper {
            width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
            pointer-events: none; 
        }

        .streaming-status {
            text-align: center; padding-top: 8px; display: none;
        }
        .streaming-status.active { display: block; }
        .streaming-indicator {
            display: inline-flex; align-items: center; background: rgba(220, 38, 38, 0.1);
            padding: 4px 12px; border-radius: 12px;
        }
        .streaming-dot {
            width: 6px; height: 6px; background: #DC2626; border-radius: 50%; margin-right: 8px;
            animation: pulse 1s infinite;
        }
        .streaming-text { font-size: 12px; color: var(--text-secondary); font-weight: 500; }

        /* SIDEBAR */
        .sidebar-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: var(--overlay); z-index: 200; opacity: 0; pointer-events: none;
            transition: opacity 0.3s;
        }
        .sidebar-overlay.open { opacity: 1; pointer-events: auto; }

        .sidebar {
            position: fixed; top: 0; left: 0; width: 80%; height: 100%; max-width: 320px;
            background: var(--sidebar-bg); z-index: 201; transform: translateX(-100%);
            transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            display: flex; flex-direction: column;
        }
        .sidebar.open { transform: translateX(0); }
        
        .sidebar-header { padding: 24px; border-bottom: 1px solid var(--border); padding-top: max(24px, env(safe-area-inset-top)); }
        .sidebar-title { font-size: 24px; font-weight: 700; color: var(--text); letter-spacing: -0.3px; }

        .new-chat-btn {
            margin: 20px; padding: 16px; border-radius: 12px; background: var(--new-chat-bg);
            color: var(--new-chat-text); border: none; display: flex; align-items: center; justify-content: center;
            font-size: 16px; font-weight: 600; cursor: pointer; font-family: var(--font-main);
        }
        .new-chat-btn ion-icon { margin-right: 8px; font-size: 20px; }

        .history-section { flex: 1; overflow-y: auto; padding: 0 20px; }
        .history-title {
            font-size: 14px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);
            margin-bottom: 12px; letter-spacing: 0.5px;
        }
        .history-item {
            display: flex; align-items: center; padding: 16px 0; border-bottom: 1px solid var(--border);
            cursor: pointer;
        }
        .history-item-info { flex: 1; overflow: hidden; }
        .history-name { font-size: 16px; font-weight: 500; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .history-date { font-size: 13px; color: var(--text-tertiary); margin-top: 4px; }
        .history-item ion-icon { color: var(--text-tertiary); font-size: 16px; }

        /* MODALS */
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: var(--overlay); z-index: 300; display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: opacity 0.2s; padding: 20px;
        }
        .modal-overlay.open { opacity: 1; pointer-events: auto; }

        .modal-content {
            background: var(--surface-elevated); width: 100%; max-width: 340px; border-radius: 20px;
            padding: 24px; box-shadow: 0 8px 16px var(--shadow); transform: scale(0.95); transition: transform 0.2s;
        }
        .modal-overlay.open .modal-content { transform: scale(1); }
        
        .modal-title { font-size: 22px; font-weight: 700; color: var(--text); margin-bottom: 24px; text-align: center; }
        
        .settings-section { margin-bottom: 24px; }
        .section-title { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .setting-row {
            display: flex; align-items: center; justify-content: space-between; padding: 16px 0;
            border-bottom: 0.5px solid var(--border); cursor: pointer;
        }
        .setting-label { font-size: 16px; color: var(--text); }
        .setting-label.danger { color: #DC2626; }
        .setting-check { width: 24px; height: 24px; border-radius: 12px; background: var(--user-bubble); display: flex; align-items: center; justify-content: center; }
        .setting-check ion-icon { color: #fff; font-size: 16px; }

        .modal-btn {
            flex: 1; padding: 16px; border-radius: 12px; border: none; font-size: 16px; font-weight: 600;
            cursor: pointer; text-align: center; transition: opacity 0.2s;
        }
        .modal-btn:active { opacity: 0.8; }
        .modal-btn.primary { background: var(--user-bubble); color: #fff; }

        /* ANIMATIONS */
        @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.5; } 100% { transform: scale(1); opacity: 1; } }
    </style>
</head>
<body data-theme="dark">

    <div id="app">
        <!-- HEADER -->
        <header class="header">
            <button class="icon-btn" id="menu-btn">
                <div style="width:18px; display:flex; flex-direction:column; gap:4px;">
                    <div style="height:2px; background:var(--text-secondary); width:100%; border-radius:1px;"></div>
                    <div style="height:2px; background:var(--text-secondary); width:100%; border-radius:1px;"></div>
                    <div style="height:2px; background:var(--text-secondary); width:100%; border-radius:1px;"></div>
                </div>
            </button>
            
            <div class="app-title">Raze AI</div>

            <button class="icon-btn" id="settings-btn">
                <ion-icon name="settings-outline"></ion-icon>
            </button>
        </header>

        <!-- CHAT CONTAINER -->
        <div class="chat-container" id="chat-container">
            <div class="empty-state" id="empty-state">
                <div class="empty-avatar">
                    <ion-icon name="sparkles" style="font-size: 32px; color: #fff;"></ion-icon>
                </div>
                <h1 class="empty-title">Raze AI</h1>
                <p class="empty-subtitle">Memorable AI that helps you code, create APIs, and solve problems.</p>
            </div>
            <div id="messages-list" style="display: none;"></div>
        </div>

        <!-- INPUT AREA -->
        <div class="input-area-container">
            <div class="input-wrapper">
                <textarea id="chat-input" placeholder="Type your message..." rows="1"></textarea>
                <button class="send-btn" id="send-btn" disabled onclick="handleSend()">
                    <div class="icon-wrapper">
                        <ion-icon name="arrow-up" id="send-icon"></ion-icon>
                    </div>
                </button>
            </div>
            <div class="streaming-status" id="streaming-status">
                <div class="streaming-indicator">
                    <div class="streaming-dot"></div>
                    <span class="streaming-text">Thinking...</span>
                </div>
            </div>
        </div>
    </div>

    <!-- SIDEBAR -->
    <div class="sidebar-overlay" id="sidebar-overlay"></div>
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h2 class="sidebar-title">Raze AI</h2>
        </div>
        <button class="new-chat-btn" id="new-chat-btn">
            <ion-icon name="add"></ion-icon>
            <span>New Chat</span>
        </button>
        <div class="history-section">
            <h3 class="history-title">History</h3>
            <div id="history-list"></div>
        </div>
    </aside>

    <!-- SETTINGS MODAL -->
    <div class="modal-overlay" id="settings-modal">
        <div class="modal-content">
            <h2 class="modal-title">Settings</h2>
            <div class="settings-section">
                <h3 class="section-title">Appearance</h3>
                <div class="setting-row" onclick="setTheme('dark')">
                    <span class="setting-label">Dark Mode</span>
                    <div class="setting-check" id="check-dark" style="display:none;"><ion-icon name="checkmark"></ion-icon></div>
                </div>
                <div class="setting-row" onclick="setTheme('light')">
                    <span class="setting-label">Light Mode</span>
                    <div class="setting-check" id="check-light" style="display:none;"><ion-icon name="checkmark"></ion-icon></div>
                </div>
                <div class="setting-row" onclick="clearAllData()">
                    <span class="setting-label danger">Clear Data</span>
                </div>
            </div>
            <button class="modal-btn primary" onclick="toggleSettings()">Done</button>
        </div>
    </div>

    <script>
        /* STATE */
        let state = {
            messages: [], // Stores objects: { role: 'user'|'assistant', content: '...' }
            inputText: '',
            isLoading: false,
            theme: 'dark', 
            showSidebar: false,
            currentSessionId: null,
            chatSessions: []
        };

        /* DOM ELEMENTS */
        const el = {
            body: document.body,
            input: document.getElementById('chat-input'),
            sendBtn: document.getElementById('send-btn'),
            chatList: document.getElementById('messages-list'),
            emptyState: document.getElementById('empty-state'),
            container: document.getElementById('chat-container'),
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebar-overlay'),
            historyList: document.getElementById('history-list'),
            settingsModal: document.getElementById('settings-modal'),
            streamingStatus: document.getElementById('streaming-status')
        };

        /* INITIALIZATION */
        function init() {
            loadTheme();
            loadChatSessions();
            
            el.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (!el.sendBtn.disabled) handleSend();
                }
            });

            el.input.addEventListener('input', (e) => {
                state.inputText = e.target.value;
                autoResizeInput();
                const hasText = state.inputText.trim().length > 0;
                el.sendBtn.disabled = !hasText;
                if (hasText) el.sendBtn.classList.add('active-glow');
                else el.sendBtn.classList.remove('active-glow');
            });
            
            document.getElementById('menu-btn').addEventListener('click', toggleSidebar);
            document.getElementById('new-chat-btn').addEventListener('click', startNewChat);
            document.getElementById('settings-btn').addEventListener('click', toggleSettings);
            el.sidebarOverlay.addEventListener('click', toggleSidebar);
        }

        /* API LOGIC */
        async function handleSend() {
            if (!state.inputText.trim()) return;

            const userText = state.inputText.trim();
            el.input.value = '';
            state.inputText = '';
            autoResizeInput();
            el.sendBtn.disabled = true;
            el.sendBtn.classList.remove('active-glow');

            // 1. User Message
            const userMsgObj = { role: "user", content: userText };
            state.messages.push(userMsgObj);
            addMessageToUI(userMsgObj);

            // 2. AI Placeholder
            const aiMsgObj = { role: "assistant", content: "" };
            state.messages.push(aiMsgObj); // Push immediately to reserve order in history
            addMessageToUI(aiMsgObj);
            scrollToBottom();

            state.isLoading = true;
            updateStreamingUI(true);

            try {
                // Send entire history to backend for "Memory"
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ history: state.messages })
                });
                
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                const replyText = data.reply || "No response generated.";
                
                // Update UI
                updateLastMessage(replyText);
                
                // Update State
                state.messages[state.messages.length - 1].content = replyText;
                
                state.isLoading = false;
                updateStreamingUI(false);
                saveCurrentSession();

            } catch (error) {
                console.error(error);
                updateLastMessage("Error: Failed to connect to Raze AI.");
                state.isLoading = false;
                updateStreamingUI(false);
            }
        };

        function updateLastMessage(text) {
            // Find the last message bubble (which is the AI one we just added)
            const bubbles = el.chatList.getElementsByClassName('message-content');
            if (bubbles.length > 0) {
                const lastBubble = bubbles[bubbles.length - 1];
                lastBubble.innerHTML = renderMainContent(text);
            }
            scrollToBottom();
        }

        function updateStreamingUI(isLoading) {
            if (isLoading) {
                el.streamingStatus.classList.add('active');
                el.sendBtn.style.background = '#666'; 
                el.sendBtn.disabled = true;
            } else {
                el.streamingStatus.classList.remove('active');
                el.sendBtn.style.background = '';
                el.sendBtn.disabled = !state.inputText.trim();
                if(state.inputText.trim().length > 0) el.sendBtn.classList.add('active-glow');
            }
        }

        /* MARKDOWN PARSING */
        function renderMainContent(text) {
            if (!text) return '<span style="color:var(--text-tertiary);">...</span>';
            const codeRegex = /```(\w*)\n?([\s\S]*?)```/g;
            const parts = [];
            let lastIndex = 0;
            let match;
            let codeIndex = 0;
            while ((match = codeRegex.exec(text)) !== null) {
                if (match.index > lastIndex) parts.push(parseInlineMarkdown(text.slice(lastIndex, match.index)));
                parts.push(renderCodeBlock(match[1], match[2].trim(), codeIndex++));
                lastIndex = match.index + match[0].length;
            }
            if (lastIndex < text.length) parts.push(parseInlineMarkdown(text.slice(lastIndex)));
            return parts.join('');
        }

        function parseInlineMarkdown(text) {
            if (!text) return '';
            let html = escapeHtml(text);
            html = html.replace(/^#### (.*$)/gim, '<span class="md-header md-h4">$1</span>');
            html = html.replace(/^### (.*$)/gim, '<span class="md-header md-h3">$1</span>');
            html = html.replace(/^## (.*$)/gim, '<span class="md-header md-h2">$1</span>');
            html = html.replace(/^# (.*$)/gim, '<span class="md-header md-h1">$1</span>');
            html = html.replace(/\*\*(.*?)\*\*/g, '<span class="md-bold">$1</span>');
            html = html.replace(/\[(.*?)\]\(.*?\)/g, '<span class="md-bold">$1</span>');
            return html.replace(/\n/g, '<br>');
        }

        function renderCodeBlock(lang, code, index) {
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span class="code-lang">${lang || 'code'}</span>
                        <button class="copy-btn" onclick="copyCode(this)">
                            <ion-icon name="copy-outline"></ion-icon> Copy
                        </button>
                    </div>
                    <pre class="code-content">${escapeHtml(code)}</pre>
                </div>`;
        }

        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        async function copyCode(btn) {
            const code = btn.closest('.code-block').querySelector('.code-content').innerText;
            try {
                await navigator.clipboard.writeText(code);
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<ion-icon name="checkmark"></ion-icon> Copied';
                btn.style.color = 'var(--user-bubble)';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.color = '';
                }, 2000);
            } catch (err) {}
        }

        /* UI MANAGEMENT */
        function addMessageToUI(msg) {
            el.emptyState.style.display = 'none';
            el.chatList.style.display = 'block';
            
            const div = document.createElement('div');
            div.className = `message-row ${msg.role === 'user' ? 'user' : 'ai'}`;
            
            let avatarHtml = '';
            if (msg.role !== 'user') {
                avatarHtml = `<div class="ai-avatar"><ion-icon name="sparkles" style="color:var(--text-secondary);"></ion-icon></div>`;
            }

            div.innerHTML = `
                ${avatarHtml}
                <div class="message-bubble">
                    <div class="message-content">
                        ${msg.content ? renderMainContent(msg.content) : '<span style="color:var(--text-tertiary);">...</span>'}
                    </div>
                </div>`;
            el.chatList.appendChild(div);
        }

        function scrollToBottom() { el.container.scrollTop = el.container.scrollHeight; }
        function autoResizeInput() {
            el.input.style.height = 'auto';
            el.input.style.height = el.input.scrollHeight + 'px';
        }

        /* SIDEBAR & HISTORY */
        function toggleSidebar() {
            state.showSidebar = !state.showSidebar;
            if (state.showSidebar) {
                el.sidebar.classList.add('open');
                el.sidebarOverlay.classList.add('open');
                renderHistory();
            } else {
                el.sidebar.classList.remove('open');
                el.sidebarOverlay.classList.remove('open');
            }
        }

        function startNewChat() {
            state.messages = [];
            state.currentSessionId = null;
            el.chatList.innerHTML = '';
            el.chatList.style.display = 'none';
            el.emptyState.style.display = 'flex';
            toggleSidebar();
        }

        function renderHistory() {
            if (state.chatSessions.length === 0) {
                el.historyList.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-tertiary);">No history yet.</div>';
                return;
            }
            el.historyList.innerHTML = state.chatSessions.map(session => `
                <div class="history-item" onclick="loadSession('${session.id}')">
                    <div class="history-item-info">
                        <div class="history-name">${escapeHtml(session.name)}</div>
                        <div class="history-date">${new Date(session.createdAt).toLocaleDateString()}</div>
                    </div>
                    <ion-icon name="chevron-forward"></ion-icon>
                </div>`).join('');
        }

        function loadSession(id) {
            const session = state.chatSessions.find(s => s.id === id);
            if (!session) return;
            state.messages = session.messages || [];
            state.currentSessionId = session.id;
            
            el.chatList.innerHTML = '';
            if (state.messages.length > 0) {
                el.emptyState.style.display = 'none';
                el.chatList.style.display = 'block';
                state.messages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = `message-row ${msg.role === 'user' ? 'user' : 'ai'}`;
                    let avatarHtml = '';
                    if (msg.role !== 'user') avatarHtml = `<div class="ai-avatar"><ion-icon name="sparkles" style="color:var(--text-secondary);"></ion-icon></div>`;
                    
                    div.innerHTML = `
                        ${avatarHtml}
                        <div class="message-bubble">
                            <div class="message-content">
                                ${renderMainContent(msg.content)}
                            </div>
                        </div>`;
                    el.chatList.appendChild(div);
                });
            } else {
                el.emptyState.style.display = 'flex';
                el.chatList.style.display = 'none';
            }
            toggleSidebar();
            scrollToBottom();
        }

        /* STORAGE & SETTINGS */
        function loadTheme() {
            const saved = localStorage.getItem('raze_theme') || 'dark';
            setTheme(saved);
        }

        function setTheme(themeName) {
            state.theme = themeName;
            el.body.setAttribute('data-theme', themeName);
            localStorage.setItem('raze_theme', themeName);
            document.getElementById('check-dark').style.display = themeName === 'dark' ? 'flex' : 'none';
            document.getElementById('check-light').style.display = themeName === 'light' ? 'flex' : 'none';
        }

        function toggleSettings() {
            const isOpen = el.settingsModal.classList.contains('open');
            el.settingsModal.classList.toggle('open');
            if (!isOpen) setTheme(state.theme);
        }

        function loadChatSessions() {
            try {
                const stored = localStorage.getItem('raze_sessions');
                if (stored) state.chatSessions = JSON.parse(stored);
            } catch (e) { console.error(e); }
        }

        function saveCurrentSession() {
            if (state.messages.length === 0) return;
            const firstUserMsg = state.messages.find(m => m.role === 'user');
            const sessionName = firstUserMsg ? (firstUserMsg.content.substring(0, 30) + '...') : 'New Chat';
            
            if (state.currentSessionId) {
                const idx = state.chatSessions.findIndex(s => s.id === state.currentSessionId);
                if (idx !== -1) {
                    state.chatSessions[idx].messages = state.messages;
                    state.chatSessions[idx].updatedAt = new Date().toISOString();
                }
            } else {
                const newSession = {
                    id: Date.now().toString(),
                    name: sessionName,
                    createdAt: new Date().toISOString(),
                    messages: state.messages
                };
                state.chatSessions.unshift(newSession);
                state.currentSessionId = newSession.id;
            }
            localStorage.setItem('raze_sessions', JSON.stringify(state.chatSessions));
        }

        function clearAllData() {
            if(confirm("Are you sure you want to clear all data?")) {
                localStorage.clear();
                location.reload();
            }
        }

        /* BOOTSTRAP */
        init();
    </script>
</body>
</html>
'''

# ==========================================
# BACKEND ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        # Frontend sends the full history
        history = data.get('history', [])
        
        if not history:
            return jsonify({'reply': 'No history provided'}), 400

        # Define System Prompt for Raze AI
        system_message = {
            "role": "system",
            "content": (
                "You are Raze AI, a smart assistant that helps users "
                "create APIs, develop tools, and solve programming problems. "
                "You remember the entire conversation and provide clear, step-by-step guidance."
            )
        }

        # Construct Payload for OpenRouter
        # Prepend system message to the user history
        messages_payload = [system_message] + history

        payload = {
            "model": MODEL,
            "messages": messages_payload
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000", 
            "X-Title": "Raze AI"
        }

        # Call OpenRouter API
        res = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        
        if res.status_code == 200:
            api_data = res.json()
            reply_text = api_data["choices"][0]["message"]["content"]
            return jsonify({'reply': reply_text})
        elif res.status_code == 402:
            return jsonify({'reply': 'Error: Payment Required. Your API key does not have access to this model.'}), 402
        else:
            return jsonify({'reply': f'Error: API returned status code {res.status_code}'}), res.status_code

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        return jsonify({'reply': 'Error: Failed to connect to the AI service.'}), 500
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'reply': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
