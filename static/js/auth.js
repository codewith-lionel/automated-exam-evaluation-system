// Authentication - Login/Signup Logic

document.addEventListener('DOMContentLoaded', () => {
    // Get elements
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginSubmitBtn = document.getElementById('loginSubmit');
    const signupSubmitBtn = document.getElementById('signupSubmit');

    // Password toggle buttons
    const passwordToggles = document.querySelectorAll('.password-toggle-btn');
    
    passwordToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            const icon = btn.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });
    });

    // Tab switching
    if (loginTab && signupTab) {
        loginTab.addEventListener('click', () => {
            loginTab.classList.add('active');
            signupTab.classList.remove('active');
            loginForm.classList.add('active');
            signupForm.classList.remove('active');
        });

        signupTab.addEventListener('click', () => {
            signupTab.classList.add('active');
            loginTab.classList.remove('active');
            signupForm.classList.add('active');
            loginForm.classList.remove('active');
        });
    }

    // Login Form Handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!validation.validateForm(loginForm)) {
                return;
            }

            const formData = {
                email: document.getElementById('loginEmail').value,
                password: document.getElementById('loginPassword').value,
                remember: document.getElementById('rememberMe')?.checked || false
            };

            try {
                loginSubmitBtn.disabled = true;
                loginSubmitBtn.innerHTML = '<span class="spinner"></span> Logging in...';

                const response = await api.post('/auth/login', formData);

                if (response.success) {
                    storage.set('user', response.user);
                    storage.set('token', response.token);
                    
                    toast.success('Login successful! Redirecting...');
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    toast.error(response.message || 'Login failed');
                    loginSubmitBtn.disabled = false;
                    loginSubmitBtn.innerHTML = 'Login';
                }
            } catch (error) {
                toast.error(error.message || 'Login failed. Please try again.');
                loginSubmitBtn.disabled = false;
                loginSubmitBtn.innerHTML = 'Login';
            }
        });
    }

    // Signup Form Handler
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!validation.validateForm(signupForm)) {
                return;
            }

            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('signupConfirmPassword').value;

            if (password !== confirmPassword) {
                validation.showError(
                    document.getElementById('signupConfirmPassword'),
                    'Passwords do not match'
                );
                return;
            }

            const formData = {
                name: document.getElementById('signupName').value,
                email: document.getElementById('signupEmail').value,
                password: password,
                role: document.getElementById('signupRole').value
            };

            try {
                signupSubmitBtn.disabled = true;
                signupSubmitBtn.innerHTML = '<span class="spinner"></span> Creating account...';

                const response = await api.post('/auth/signup', formData);

                if (response.success) {
                    toast.success('Account created successfully! Please login.');
                    
                    // Switch to login tab
                    loginTab.click();
                    
                    // Pre-fill email
                    document.getElementById('loginEmail').value = formData.email;
                    
                    signupForm.reset();
                    signupSubmitBtn.disabled = false;
                    signupSubmitBtn.innerHTML = 'Sign Up';
                } else {
                    toast.error(response.message || 'Signup failed');
                    signupSubmitBtn.disabled = false;
                    signupSubmitBtn.innerHTML = 'Sign Up';
                }
            } catch (error) {
                toast.error(error.message || 'Signup failed. Please try again.');
                signupSubmitBtn.disabled = false;
                signupSubmitBtn.innerHTML = 'Sign Up';
            }
        });
    }

    // Clear validation errors on input
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            validation.clearError(input);
        });
    });
});

// Logout Function
const logout = () => {
    storage.remove('user');
    storage.remove('token');
    toast.info('Logged out successfully');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
};

// Check if user is authenticated
const isAuthenticated = () => {
    return storage.get('token') !== null;
};

// Get current user
const getCurrentUser = () => {
    return storage.get('user');
};

// Protect page - redirect to login if not authenticated
const protectPage = () => {
    if (!isAuthenticated()) {
        window.location.href = '/';
    }
};
