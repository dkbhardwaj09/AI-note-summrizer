document.addEventListener('DOMContentLoaded', () => {
    // --- Firebase Configuration ---
    const firebaseConfig = {
      apiKey: "AIzaSyBKiEnoYJlmF5kI-p24p3N9PjaihUUYwWI",
      authDomain: "neurosync-ec6ea.firebaseapp.com",
      projectId: "neurosync-ec6ea",
      storageBucket: "neurosync-ec6ea.firebasestorage.app",
      messagingSenderId: "677353155879",
      appId: "1:677353155879:web:e4c2d5b89a33caa900cd02",
      measurementId: "G-D48FLLWDM0"
    };

    // --- Initialize Firebase ---
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();

    // --- Globals ---
    const API_URL = window.location.origin;
    let FIREBASE_ID_TOKEN = localStorage.getItem('firebaseIdToken');
    let CURRENT_FILE_ID = null;
    let CHAT_HISTORY = [];

    // --- DOM Elements ---
    const logoutBtn = document.getElementById('logout-btn');
    const pdfSessionsList = document.getElementById('pdf-sessions-list');
    const welcomeView = document.getElementById('welcome-view');
    const chatView = document.getElementById('chat-view');
    const chatTitle = document.getElementById('chat-title').querySelector('span');
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    const uploadForm = document.getElementById('upload-form');
    const pdfFileInput = document.getElementById('pdf-file');
    const uploadStatus = document.getElementById('upload-status');

    // --- Auth Check ---
    auth.onAuthStateChanged(user => {
        if (user) {
            // User is signed in.
            user.getIdToken().then(token => {
                FIREBASE_ID_TOKEN = token;
                localStorage.setItem('firebaseIdToken', token);
                initializeApp();
            });
        } else {
            // No user is signed in. Redirect to login.
            localStorage.removeItem('firebaseIdToken');
            window.location.href = '/login.html';
        }
    });

    // --- Main App Logic ---
    const initializeApp = () => {
        setupEventListeners();
        fetchPdfSessions();
    };

    const setupEventListeners = () => {
        logoutBtn.addEventListener('click', () => {
            auth.signOut();
        });

        uploadForm.addEventListener('submit', handlePdfUpload);
        chatForm.addEventListener('submit', handleChatSubmit);
        pdfSessionsList.addEventListener('click', handleSessionClick);
    };

    const getAuthHeaders = () => {
        return { 'Authorization': `Bearer ${FIREBASE_ID_TOKEN}` };
    };

    // --- PDF Session Management ---
    const fetchPdfSessions = async () => {
        try {
            const response = await fetch(`${API_URL}/api/rag/sessions`, { headers: getAuthHeaders() });
            if (!response.ok) throw new Error('Failed to fetch sessions.');
            const sessions = await response.json();
            renderPdfSessions(sessions);
        } catch (error) {
            console.error('Error fetching PDF sessions:', error);
            pdfSessionsList.innerHTML = '<p class="error">Could not load sessions.</p>';
        }
    };

    const renderPdfSessions = (sessions) => {
        pdfSessionsList.innerHTML = '';
        if (sessions.length === 0) {
            pdfSessionsList.innerHTML = '<p>No PDFs uploaded yet.</p>';
            return;
        }
        sessions.forEach(session => {
            const sessionEl = document.createElement('div');
            sessionEl.className = 'session-item';
            sessionEl.dataset.fileId = session.file_id;
            sessionEl.dataset.filename = session.filename;
            sessionEl.textContent = session.filename;
            pdfSessionsList.appendChild(sessionEl);
        });
    };

    const handlePdfUpload = async (e) => {
        e.preventDefault();
        if (pdfFileInput.files.length === 0) {
            alert('Please select a PDF file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', pdfFileInput.files[0]);

        uploadStatus.textContent = 'Uploading and processing...';
        uploadStatus.style.color = 'orange';

        try {
            const response = await fetch(`${API_URL}/api/rag/upload`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Upload failed.');

            uploadStatus.textContent = `Success: ${result.filename}`;
            uploadStatus.style.color = 'green';
            uploadForm.reset();
            fetchPdfSessions(); // Refresh the list
        } catch (error) {
            console.error('Upload error:', error);
            uploadStatus.textContent = `Error: ${error.message}`;
            uploadStatus.style.color = 'red';
        }
    };

    const handleSessionClick = (e) => {
        if (e.target.classList.contains('session-item')) {
            // Highlight the selected item
            document.querySelectorAll('.session-item').forEach(item => item.classList.remove('active'));
            e.target.classList.add('active');

            CURRENT_FILE_ID = e.target.dataset.fileId;
            const filename = e.target.dataset.filename;

            // Switch to chat view
            welcomeView.classList.add('hidden');
            chatView.classList.remove('hidden');

            chatTitle.textContent = filename;
            chatBox.innerHTML = `<p class="bot-message">Chatting with ${filename}. Ask a question!</p>`;
            CHAT_HISTORY = []; // Reset chat history for the new session
        }
    };

    // --- Chat Logic ---
    const handleChatSubmit = async (e) => {
        e.preventDefault();
        const question = chatInput.value.trim();
        if (!question || !CURRENT_FILE_ID) return;

        addMessageToChatbox('user', question);
        const userMessage = question;
        chatInput.value = '';
        chatInput.disabled = true;

        try {
            const response = await fetch(`${API_URL}/api/rag/chat/${CURRENT_FILE_ID}`, {
                method: 'POST',
                headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMessage, chat_history: CHAT_HISTORY })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Chat request failed.');

            CHAT_HISTORY = result.chat_history;
            addMessageToChatbox('bot', result.answer);

        } catch (error) {
            console.error('Chat error:', error);
            addMessageToChatbox('bot', `Error: ${error.message}`);
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    };

    const addMessageToChatbox = (sender, message) => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };
});