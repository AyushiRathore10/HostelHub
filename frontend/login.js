/*
  login.js
  --------
  This file runs on the login page (index.html).
  It handles:
    1. Role selection (Admin / Student card click)
    2. Form submission → sends data to FastAPI backend
    3. Saves user info in localStorage
    4. Redirects to the right dashboard
*/

const API_URL = 'http://127.0.0.1:8000';

// Grab HTML elements by their IDs
const adminCard        = document.getElementById('admin-card');
const studentCard      = document.getElementById('student-card');
const selectedRoleInput= document.getElementById('selected-role');
const formHeading      = document.getElementById('form-heading');
const loginForm        = document.getElementById('login-form');
const usernameInput    = document.getElementById('username');
const passwordInput    = document.getElementById('password');
const errorMessage     = document.getElementById('error-message');

// Student card is highlighted by default
studentCard.classList.add('active');

// When Admin card is clicked
adminCard.addEventListener('click', function () {
    adminCard.classList.add('active');
    studentCard.classList.remove('active');
    selectedRoleInput.value = 'admin';
    formHeading.textContent = 'Admin Login';
    usernameInput.placeholder = 'Enter admin username';
    errorMessage.textContent  = '';
});

// When Student card is clicked
studentCard.addEventListener('click', function () {
    studentCard.classList.add('active');
    adminCard.classList.remove('active');
    selectedRoleInput.value = 'student';
    formHeading.textContent = 'Student Login';
    usernameInput.placeholder = 'Enter your Roll Number (e.g. CS202401)';
    errorMessage.textContent  = '';
});

// Form Submit → call FastAPI /api/auth/login
loginForm.addEventListener('submit', async function (e) {
    e.preventDefault();   // Stop browser from refreshing the page

    const role     = selectedRoleInput.value;
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (password.length < 4) {
        errorMessage.style.color = '#d93025';
        errorMessage.textContent = 'Password must be at least 4 characters.';
        return;
    }

    errorMessage.style.color = '#1e3c72';
    errorMessage.textContent = '⏳ Contacting server...';

    try {
        /*
          fetch() sends an HTTP request.
          method: 'POST'  → we are SENDING data, not just reading a page
          headers         → tells server we are sending JSON
          body            → the actual data as a JSON string
        */
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ role, username, password })
        });

        const result = await response.json();  // Parse the JSON response from FastAPI

        if (result.success) {
            errorMessage.style.color = '#137333';
            errorMessage.textContent = `✅ ${result.message}. Welcome, ${result.name}!`;

            // Save in localStorage — like a temporary memory in the browser
            // These values are read on every dashboard page
            localStorage.setItem('userRole', result.role);
            localStorage.setItem('userName', result.name);

            if (result.role === 'student') {
                localStorage.setItem('userRoll', result.roll_no); // needed to load student-specific data
            }

            // Wait 1 second then redirect
            setTimeout(function () {
                if (result.role === 'admin') {
                    window.location.href = 'admin/dashboard.html';
                } else {
                    window.location.href = 'student/dashboard.html';
                }
            }, 1000);

        } else {
            errorMessage.style.color = '#d93025';
            errorMessage.textContent = '❌ ' + result.message;
        }

    } catch (error) {
        errorMessage.style.color = '#d93025';
        errorMessage.textContent = '🔴 Cannot reach server. Make sure FastAPI is running on port 8000!';
        console.error(error);
    }
});
