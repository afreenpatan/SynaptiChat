const loginForm = document.getElementById("loginForm");

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

const togglePassword =
    document.getElementById("togglePassword");

const loginError =
    document.getElementById("loginError");


// ===============================
// SHOW / HIDE PASSWORD
// ===============================

togglePassword.addEventListener("click", function () {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        togglePassword.textContent = "🙈";

    } else {

        passwordInput.type = "password";

        togglePassword.textContent = "👁";

    }

});


// ===============================
// PASSWORD VALIDATION
// ===============================

passwordInput.addEventListener("input", function () {

    const password = passwordInput.value;

    const length = document.getElementById("length");
    const uppercase = document.getElementById("uppercase");
    const number = document.getElementById("number");
    const special = document.getElementById("special");


    // 8 characters
    if (password.length >= 8) {

        length.textContent = "✓ At least 8 characters";

    } else {

        length.textContent = "○ At least 8 characters";

    }


    // Uppercase
    if (/[A-Z]/.test(password)) {

        uppercase.textContent = "✓ One uppercase letter";

    } else {

        uppercase.textContent = "○ One uppercase letter";

    }


    // Number
    if (/[0-9]/.test(password)) {

        number.textContent = "✓ One number";

    } else {

        number.textContent = "○ One number";

    }


    // Special character
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {

        special.textContent = "✓ One special character";

    } else {

        special.textContent = "○ One special character";

    }

});


// ===============================
// LOGIN
// ===============================

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    loginError.textContent = "";


    const email = emailInput.value.trim();

    const password = passwordInput.value;


    // Validate password
    const validPassword =
        password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[0-9]/.test(password) &&
        /[!@#$%^&*(),.?":{}|<>]/.test(password);


    if (!validPassword) {

        loginError.textContent =
            "Please enter a valid password.";

        return;

    }


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );


        const data = await response.json();


        if (response.ok) {

            // Save login status
            localStorage.setItem(
                "synaptichat_logged_in",
                "true"
            );

            localStorage.setItem(
                "synaptichat_email",
                email
            );


            // Go to home
            window.location.href = "home.html";

        } else {

            loginError.textContent =
                data.detail || "Invalid email or password.";

        }

    } catch (error) {

        console.error(error);

        loginError.textContent =
            "Unable to connect to the backend.";

    }

});


// ===============================
// FORGOT PASSWORD
// ===============================

document
    .getElementById("forgotPassword")
    .addEventListener("click", function (event) {

        event.preventDefault();

        alert(
            "Password reset functionality will be added soon."
        );

    });


// ===============================
// SIGN UP
// ===============================

document
    .getElementById("signupLink")
    .addEventListener("click", function (event) {

        event.preventDefault();

        alert(
            "Account creation functionality will be added soon."
        );

    });