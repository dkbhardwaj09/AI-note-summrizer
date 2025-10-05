document.addEventListener('DOMContentLoaded', () => {
    // --- Globals ---
    const API_URL = window.location.origin;
    let FIREBASE_ID_TOKEN = localStorage.getItem('firebaseIdToken') || '';
    let CURRENT_FILE_ID = '';
    let CHAT_HISTORY = [];

    // --- DOM Elements ---
    const tokenTextarea = document.getElementById('firebase-token');
    const saveTokenBtn = document.getElementById('save-token-btn');
    const authStatus = document.getElementById('auth-status');

    const noteForm = document.getElementById('note-form');
    const noteTitleInput = document.getElementById('note-title');
    const noteDescInput = document.getElementById('note-desc');
    const noteImportantInput = document.getElementById('note-important');
    const notesList = document.getElementById('notes-list');

    const uploadForm = document.getElementById('upload-form');
    const pdfFileInput = document.getElementById('pdf-file');
    const uploadStatus = document.getElementById('upload-status');
    const currentFileIdSpan = document.getElementById('current-file-id');

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatBox = document.getElementById('chat-box');

    // --- Helper Functions ---
    const getAuthHeaders = () => {
        if (!FIREBASE_ID_TOKEN) {
            alert('Firebase ID Token is not set. Please paste it in the Authentication section.');
            return null;
        }
        return {
            'Authorization': `Bearer ${FIREBASE_ID_TOKEN}`
        };
    };

    const addMessageToChatbox = (sender, message) => {
        const messageElement = document.createElement('p');
        messageElement.className = sender === 'user' ? 'user-message' : 'bot-message';
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
    };

    // --- Authentication ---
    const updateAuthStatus = () => {
        if (FIREBASE_ID_TOKEN) {
            authStatus.textContent = 'Status: Token is Set.';
            authStatus.style.color = 'green';
            tokenTextarea.value = FIREBASE_ID_TOKEN;
        } else {
            authStatus.textContent = 'Status: No Token Set';
            authStatus.style.color = 'red';
        }
    };

    saveTokenBtn.addEventListener('click', () => {
        FIREBASE_ID_TOKEN = tokenTextarea.value.trim();
        if (FIREBASE_ID_TOKEN) {
            localStorage.setItem('firebaseIdToken', FIREBASE_ID_TOKEN);
            updateAuthStatus();
            fetchNotes(); // Fetch notes with the new token
        } else {
            alert('Please paste a token before saving.');
        }
    });

    // --- Notes ---
    const fetchNotes = async () => {
        const headers = getAuthHeaders();
        if (!headers) return;

        try {
            const response = await fetch(`${API_URL}/api/notes`, { headers });
            if (!response.ok) {
                throw new Error(`Failed to fetch notes. Status: ${response.status}`);
            }
            const notes = await response.json();
            renderNotes(notes);
        } catch (error) {
            console.error('Error fetching notes:', error);
            notesList.innerHTML = `<p class="error">Error fetching notes. Check token or console.</p>`;
        }
    };

    const renderNotes = (notes) => {
        notesList.innerHTML = '';
        if (notes.length === 0) {
            notesList.innerHTML = '<p>No notes found. Add one above!</p>';
            return;
        }
        notes.forEach(note => {
            const noteEl = document.createElement('div');
            noteEl.className = 'note-item';
            noteEl.innerHTML = `
                <div>
                    <strong>${note.title}</strong> ${note.important ? ' (Important)' : ''}
                    <p>${note.desc}</p>
                </div>
                <button data-id="${note.id}" class="delete-btn">Delete</button>
            `;
            notesList.appendChild(noteEl);
        });
    };

    noteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const headers = getAuthHeaders();
        if (!headers) return;

        const noteData = {
            title: noteTitleInput.value,
            desc: noteDescInput.value,
            important: noteImportantInput.checked
        };

        try {
            const response = await fetch(`${API_URL}/api/notes`, {
                method: 'POST',
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
            if (!response.ok) {
                throw new Error('Failed to create note.');
            }
            noteForm.reset();
            fetchNotes(); // Refresh list
        } catch (error) {
            console.error('Error creating note:', error);
            alert('Failed to create note.');
        }
    });

    notesList.addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const noteId = e.target.dataset.id;
            const headers = getAuthHeaders();
            if (!headers) return;

            if (confirm('Are you sure you want to delete this note?')) {
                try {
                    const response = await fetch(`${API_URL}/api/notes/${noteId}`, {
                        method: 'DELETE',
                        headers
                    });
                    if (!response.ok) {
                        throw new Error('Failed to delete note.');
                    }
                    fetchNotes(); // Refresh list
                } catch (error) {
                    console.error('Error deleting note:', error);
                    alert('Failed to delete note.');
                }
            }
        }
    });

    // --- RAG PDF Chat ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const headers = getAuthHeaders();
        if (!headers) return;
        if (pdfFileInput.files.length === 0) {
            alert('Please select a PDF file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', pdfFileInput.files[0]);

        uploadStatus.textContent = 'Uploading and processing...';
        uploadStatus.style.color = 'orange';

        try {
            const response = await fetch(`${API_URL}/api/rag/upload`, {
                method: 'POST',
                headers,
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to upload PDF.');
            }

            CURRENT_FILE_ID = result.file_id;
            CHAT_HISTORY = []; // Reset history for new file
            currentFileIdSpan.textContent = CURRENT_FILE_ID;
            uploadStatus.textContent = `Successfully processed: ${result.filename}`;
            uploadStatus.style.color = 'green';
            chatInput.disabled = false;
            sendChatBtn.disabled = false;
            chatBox.innerHTML = '<p class="bot-message">You can now chat with your PDF.</p>';

        } catch (error) {
            console.error('Error uploading PDF:', error);
            uploadStatus.textContent = `Error: ${error.message}`;
            uploadStatus.style.color = 'red';
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = chatInput.value.trim();
        if (!question || !CURRENT_FILE_ID) return;

        const headers = getAuthHeaders();
        if (!headers) return;

        addMessageToChatbox('user', question);
        chatInput.value = '';
        sendChatBtn.disabled = true; // Disable while waiting for response

        try {
            const response = await fetch(`${API_URL}/api/rag/chat/${CURRENT_FILE_ID}`, {
                method: 'POST',
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, chat_history: CHAT_HISTORY })
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to get chat response.');
            }

            CHAT_HISTORY = result.chat_history;
            addMessageToChatbox('bot', result.answer);

        } catch (error) {
            console.error('Chat error:', error);
            addMessageToChatbox('bot', `Error: ${error.message}`);
        } finally {
            sendChatBtn.disabled = false; // Re-enable button
        }
    });


    // --- Initial Load ---
    updateAuthStatus();
    if (FIREBASE_ID_TOKEN) {
        fetchNotes();
    }
});