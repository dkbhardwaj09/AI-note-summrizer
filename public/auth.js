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

    // --- DOM Elements ---
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const errorMessage = document.getElementById('error-message');

    // --- Event Listeners ---
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        auth.signInWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed in
                handleAuthSuccess(userCredential.user);
            })
            .catch((error) => {
                errorMessage.textContent = error.message;
            });
    });

    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        auth.createUserWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed up and signed in
                handleAuthSuccess(userCredential.user);
            })
            .catch((error) => {
                errorMessage.textContent = error.message;
            });
    });

    // --- Helper Function ---
    const handleAuthSuccess = (user) => {
        user.getIdToken().then((token) => {
            // Store the token and redirect to the main dashboard
            localStorage.setItem('firebaseIdToken', token);
            window.location.href = '/'; // Redirect to the root which serves index.html
        });
    };
});