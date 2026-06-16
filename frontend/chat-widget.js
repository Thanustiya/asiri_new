/* frontend/chat-widget.js
   Asiri Perera AI Chatbot Widget
   Embed with: <script src="chat-widget.js"></script>
*/
(function () {
  'use strict';

  const BML_API = window.BML_CHAT_API || window.location.origin;
  const WIDGET_ASSET_BASE = document.currentScript && document.currentScript.src
    ? new URL('.', document.currentScript.src).href.replace(/\/$/, '')
    : BML_API + '/static';
  const USE_WEBSOCKET = true;
  const REQUEST_TIMEOUT_MS = 25000;

  // ── State ──────────────────────────────────────────────────────────────
  let sessionId = null;
  let ws = null;
  let isOpen = false;
  let isBotTyping = false;
  let isSessionClosed = false;
  let unreadCount = 0;
  let wsReconnectTimer = null;
  let responseTimeoutTimer = null;
  let lastUserInput = '';

  // ── Build DOM ──────────────────────────────────────────────────────────
  function buildWidget() {
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = WIDGET_ASSET_BASE + '/chat-widget.css';
    document.head.appendChild(link);

    // Chat toggle button
    document.body.insertAdjacentHTML('beforeend', `
      <button id="bml-chat-button" aria-label="Open AI Chat" title="Chat with Asiri Perera AI">
        <svg id="bml-chat-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4a2 2 0 00-2 2v13a2 2 0 002 2h3v3l5.5-3H20a2 2 0 002-2V4a2 2 0 00-2-2z"/>
        </svg>
        <svg id="bml-close-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="display:none">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
        <div id="bml-chat-badge"></div>
      </button>

      <div id="bml-chat-window" role="dialog" aria-label="Asiri Perera AI Chat">
        <div id="bml-chat-header">
          <div class="bml-header-avatar">🎓</div>
          <div class="bml-header-info">
            <h3>Asiri Perera AI Assistant</h3>
            <p><span class="bml-status-dot" id="bml-status-dot"></span>
               <span id="bml-status-text">Online · Typically replies instantly</span></p>
          </div>
          <button class="bml-header-close" id="bml-close-btn" aria-label="Close chat">✕</button>
        </div>

        <div id="bml-messages" aria-live="polite"></div>

        <div id="bml-typing">
          <div class="bml-msg-avatar">🎓</div>
          <div class="bml-typing-bubble">
            <div class="bml-dot"></div>
            <div class="bml-dot"></div>
            <div class="bml-dot"></div>
          </div>
        </div>

        <div id="bml-quick-replies"></div>

        <div id="bml-input-area">
          <textarea
            id="bml-user-input"
            placeholder="Type your message…"
            rows="1"
            aria-label="Type your message"
            maxlength="500"
          ></textarea>
          <button id="bml-send-btn" aria-label="Send message">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>

        <div class="bml-chat-footer">
          Powered by Asiri Perera AI · <a href="https://www.bmlcollege.com" target="_blank">bmlcollege.com</a>
        </div>
      </div>
    `);

    // Events
    document.getElementById('bml-chat-button').addEventListener('click', toggleChat);
    document.getElementById('bml-close-btn').addEventListener('click', closeChat);
    document.getElementById('bml-send-btn').addEventListener('click', sendMessage);

    const input = document.getElementById('bml-user-input');
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    input.addEventListener('input', autoResize);
  }

  function autoResize() {
    const el = document.getElementById('bml-user-input');
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 100) + 'px';
  }

  // ── Toggle ─────────────────────────────────────────────────────────────
  function toggleChat() { isOpen ? closeChat() : openChat(); }

  function openChat() {
    isOpen = true;
    document.getElementById('bml-chat-window').classList.add('open');
    document.getElementById('bml-chat-icon').style.display = 'none';
    document.getElementById('bml-close-icon').style.display = 'block';
    clearBadge();
    document.getElementById('bml-user-input').focus();

    if (!sessionId) startSession();
  }

  function closeChat() {
    isOpen = false;
    document.getElementById('bml-chat-window').classList.remove('open');
    document.getElementById('bml-chat-icon').style.display = 'block';
    document.getElementById('bml-close-icon').style.display = 'none';
  }


  function clearResponseTimeout() {
    clearTimeout(responseTimeoutTimer);
    responseTimeoutTimer = null;
  }

  function startResponseTimeout() {
    clearResponseTimeout();
    responseTimeoutTimer = setTimeout(() => {
      hideTyping();
      appendBotMessage(
        "This is taking longer than expected. Please try a specific service question, or contact WhatsApp: +94 717 798989.",
        []
      );
    }, REQUEST_TIMEOUT_MS);
  }

  async function fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  function clearBadge() {
    unreadCount = 0;
    const badge = document.getElementById('bml-chat-badge');
    badge.style.display = 'none';
    badge.textContent = '';
  }

  function bumpBadge() {
    if (!isOpen) {
      unreadCount++;
      const badge = document.getElementById('bml-chat-badge');
      badge.style.display = 'flex';
      badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
    }
  }

  // ── Session ────────────────────────────────────────────────────────────
  async function startSession() {
    try {
      const res = await fetchWithTimeout(BML_API + '/api/chat/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: 'web' })
      });
      const data = await res.json();
      sessionId = data.session_id;

      appendBotMessage(data.welcome_message, data.quick_replies);

      if (USE_WEBSOCKET) connectWebSocket();
    } catch (e) {
      appendBotMessage(
        "Welcome to the Asiri Perera Global Services AI Assistant. I am having trouble connecting to the live chat service right now. Please try again in a moment or contact WhatsApp: +94 717 798989.",
        []
      );
    }
  }

  // ── WebSocket ──────────────────────────────────────────────────────────
  function connectWebSocket() {
    if (!sessionId) return;
    clearTimeout(wsReconnectTimer);
    const wsUrl = BML_API.replace('http', 'ws') + `/api/chat/ws/${sessionId}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('BML WS connected');
      // Heartbeat
      setInterval(() => { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' })); }, 25000);
    };

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      handleWsMessage(payload);
    };

    ws.onclose = () => {
      console.log('BML WS disconnected — reconnecting in 3s');
      wsReconnectTimer = setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => ws.close();
  }

  function handleWsMessage(payload) {
    hideTyping();
    switch (payload.type) {
      case 'typing':
        if (payload.status) showTyping(); else hideTyping();
        break;
      case 'message':
        handleBotResponse(payload.data);
        break;
      case 'agent_message':
        handleAgentResponse(payload.data);
        break;
      case 'session_closed':
        showSessionClosed(payload.message);
        break;
    }
  }

  // ── Send Message ───────────────────────────────────────────────────────
  async function sendMessage() {
    const input = document.getElementById('bml-user-input');
    const text = input.value.trim();
    if (!text || isBotTyping || isSessionClosed) return;

    input.value = '';
    input.style.height = 'auto';
    clearQuickReplies();
    appendUserMessage(text);
    showTyping();
    lastUserInput = text;

    if (!sessionId) { await startSession(); return; }

    if (ws && ws.readyState === WebSocket.OPEN) {
      startResponseTimeout();
      ws.send(JSON.stringify({ type: 'message', message: text }));
    } else {
      // Fallback to REST
      try {
        const res = await fetchWithTimeout(BML_API + '/api/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, message: text })
        });
        const data = await res.json();
        hideTyping();
        handleBotResponse(data);
      } catch (e) {
        hideTyping();
        appendBotMessage("Sorry, I had trouble connecting. Please try again.", []);
      }
    }
  }

  function handleBotResponse(data) {
    clearResponseTimeout();
    hideTyping();
    if (!data.message && data.status === 'with_agent') return;

    if (data.status === 'with_agent') {
      appendSystemMessage(data.message);
    } else {
      appendBotMessage(data.message, data.quick_replies || []);
    }

    if (data.status === 'closed') {
      showSessionClosed('');
    }

    bumpBadge();
  }

  function handleAgentResponse(data) {
    clearResponseTimeout();
    hideTyping();
    appendAgentMessage(data.message);
    bumpBadge();
  }

  // ── Render Messages ────────────────────────────────────────────────────
  function appendUserMessage(text) {
    const msgs = document.getElementById('bml-messages');
    const time = formatTime(new Date());
    const div = document.createElement('div');
    div.className = 'bml-msg-group user';
    div.innerHTML = `
      <div class="bml-msg-row">
        <div class="bml-bubble">${escapeHtml(text)}</div>
      </div>
      <div class="bml-msg-time">${time}</div>
    `;
    msgs.appendChild(div);
    scrollToBottom();
  }

  function appendBotMessage(text, quickReplies = []) {
    isBotTyping = false;
    const msgs = document.getElementById('bml-messages');
    const time = formatTime(new Date());
    const div = document.createElement('div');
    div.className = 'bml-msg-group bot';
    div.innerHTML = `
      <div class="bml-msg-row">
        <div class="bml-msg-avatar">🎓</div>
        <div class="bml-bubble">${formatMarkdown(text)}</div>
      </div>
      <div class="bml-msg-time">${time}</div>
    `;
    msgs.appendChild(div);
    scrollToBottom();
    if (quickReplies && quickReplies.length > 0) renderQuickReplies(quickReplies);
  }

  function appendAgentMessage(text) {
    const msgs = document.getElementById('bml-messages');
    const time = formatTime(new Date());
    const div = document.createElement('div');
    div.className = 'bml-msg-group agent';
    div.innerHTML = `
      <div class="bml-msg-row">
        <div class="bml-msg-avatar agent">👤</div>
        <div class="bml-bubble">${formatMarkdown(text)}</div>
      </div>
      <div class="bml-msg-time">${time}</div>
    `;
    msgs.appendChild(div);
    scrollToBottom();
  }

  function appendSystemMessage(text) {
    const msgs = document.getElementById('bml-messages');
    const div = document.createElement('div');
    div.className = 'bml-msg-group system';
    div.innerHTML = `
      <div class="bml-bubble">${formatMarkdown(text)}</div>
    `;
    msgs.appendChild(div);
    scrollToBottom();
  }

  function showSessionClosed(msg) {
    isSessionClosed = true;
    const inputArea = document.getElementById('bml-input-area');
    const existing = document.querySelector('.bml-session-closed');
    if (!existing) {
      const div = document.createElement('div');
      div.className = 'bml-session-closed';
      div.innerHTML = '✅ Chat session ended. <a href="https://www.bmlcollege.com" target="_blank">Visit our website</a>';
      inputArea.parentNode.insertBefore(div, inputArea);
    }
    const input = document.getElementById('bml-user-input');
    const btn = document.getElementById('bml-send-btn');
    input.disabled = true;
    btn.disabled = true;
    if (msg) appendSystemMessage(msg);
  }

  // ── Quick Replies ──────────────────────────────────────────────────────
  function renderQuickReplies(replies) {
    const qr = document.getElementById('bml-quick-replies');
    qr.innerHTML = '';
    replies.forEach(reply => {
      const btn = document.createElement('button');
      btn.className = 'bml-quick-btn';
      btn.textContent = reply;
      btn.addEventListener('click', () => {
        clearQuickReplies();
        appendUserMessage(reply);
        showTyping();
        sendQuickReply(reply);
      });
      qr.appendChild(btn);
    });
  }

  function clearQuickReplies() {
    document.getElementById('bml-quick-replies').innerHTML = '';
  }

  async function sendQuickReply(text) {
    if (!sessionId) return;
    if (ws && ws.readyState === WebSocket.OPEN) {
      startResponseTimeout();
      ws.send(JSON.stringify({ type: 'message', message: text }));
    } else {
      try {
        const res = await fetchWithTimeout(BML_API + '/api/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, message: text })
        });
        const data = await res.json();
        hideTyping();
        handleBotResponse(data);
      } catch (e) {
        hideTyping();
        appendBotMessage("Sorry, something went wrong. Please try again.", []);
      }
    }
  }

  // ── Typing Indicator ───────────────────────────────────────────────────
  function showTyping() {
    isBotTyping = true;
    const t = document.getElementById('bml-typing');
    t.style.display = 'flex';
    scrollToBottom();
  }

  function hideTyping() {
    isBotTyping = false;
    document.getElementById('bml-typing').style.display = 'none';
  }

  // ── Utilities ──────────────────────────────────────────────────────────
  function scrollToBottom() {
    const msgs = document.getElementById('bml-messages');
    requestAnimationFrame(() => { msgs.scrollTop = msgs.scrollHeight; });
  }

  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatMarkdown(text) {
    // Escape HTML first
    let t = escapeHtml(text);
    // **bold**
    t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // *italic*
    t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // Newlines
    t = t.replace(/\n/g, '<br>');
    // Links (already escaped, so look for href patterns)
    t = t.replace(/🔗 (https?:\/\/[^\s<]+)/g, '🔗 <a href="$1" target="_blank" style="color:#2563eb">$1</a>');
    return t;
  }

  // ── Init ───────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildWidget);
  } else {
    buildWidget();
  }

  // Expose for programmatic control
  window.BMLChat = { open: openChat, close: closeChat, toggle: toggleChat };

})();