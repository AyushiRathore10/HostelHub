// 1. Get HTML elements by their IDs
const adminCard = document.getElementById('admin-card');
const studentCard = document.getElementById('student-card');
const selectedRoleInput = document.getElementById('selected-role');
const formHeading = document.getElementById('form-heading');
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const errorMessage = document.getElementById('error-message');

// 2. Set default active card on page load (Student is selected by default)
studentCard.classList.add('active');

// 3. When Admin Card is clicked
adminCard.addEventListener('click', function () {
    // Highlight Admin card, remove highlight from Student card
    adminCard.classList.add('active');
    studentCard.classList.remove('active');

    // Update the hidden role value and the heading text
    selectedRoleInput.value = 'admin';
    formHeading.textContent = 'Admin Login';

    // Clear any previous error messages
    errorMessage.textContent = '';
});

// 4. When Student Card is clicked
studentCard.addEventListener('click', function () {
    // Highlight Student card, remove highlight from Admin card
    studentCard.classList.add('active');
    adminCard.classList.remove('active');

    // Update the hidden role value and the heading text
    selectedRoleInput.value = 'student';
    formHeading.textContent = 'Student Login';

    // Clear any previous error messages
    errorMessage.textContent = '';
});

// 5. Handle Login Form Submit (Connect to FastAPI Backend!)
loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const role = selectedRoleInput.value;
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    // Basic Validation: Check password length
    if (password.length < 4) {
        errorMessage.style.color = '#d93025';
        errorMessage.textContent = 'Password must be at least 4 characters long.';
        return;
    }

    // Show loading state
    errorMessage.style.color = '#1e3c72';
    errorMessage.textContent = 'Contacting backend server...';

    try {
        // Send POST request to our running FastAPI server!
        const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                role: role,
                username: username,
                password: password
            })
        });

        // Read JSON response from FastAPI
        const result = await response.json();

        // If backend says success: True
        if (result.success) {
            errorMessage.style.color = '#137333';
            errorMessage.textContent = `${result.message} Welcome, ${result.name}!`;

            // Save user info in browser memory
            localStorage.setItem('userRole', result.role);
            localStorage.setItem('userName', result.name);

            // Redirect to appropriate dashboard after 1 second
            setTimeout(function () {
                if (result.role === 'admin') {
                    window.location.href = 'admin/dashboard.html';
                } else {
                    window.location.href = 'student/dashboard.html';
                }
            }, 1000);

        } else {
            // Backend rejected credentials (Invalid password)
            errorMessage.style.color = '#d93025';
            errorMessage.textContent = result.message;
        }

    } catch (error) {
        // If Python server is offline or network fails
        errorMessage.style.color = '#d93025';
        errorMessage.textContent = 'Cannot reach backend server. Make sure FastAPI is running on port 8000!';
        console.error('Connection error:', error);
    }
});


