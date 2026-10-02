// ===============================
// SUPABASE CONFIGURATION
// ===============================

const SUPABASE_URL =
    "https://ncmzxckwmqxeedgvnnur.supabase.co";

const SUPABASE_PUBLISHABLE_KEY =
    "sb_publishable_aPG_CYVW5l8p9XHxBkZegw_P_AVSQSl";


const supabaseClient =
    supabase.createClient(
        SUPABASE_URL,
        SUPABASE_PUBLISHABLE_KEY
    );


// ===============================
// ELEMENTS
// ===============================

const loginForm =
    document.getElementById("loginForm");

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

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
// PASSWORD VALIDATION DISPLAY
// ===============================

passwordInput.addEventListener("input", function () {

    const password =
        passwordInput.value;

    const length =
        document.getElementById("length");

    const uppercase =
        document.getElementById("uppercase");

    const number =
        document.getElementById("number");

    const special =
        document.getElementById("special");


    // 8 characters

    if (password.length >= 8) {

        length.textContent =
            "✓ At least 8 characters";

    } else {

        length.textContent =
            "○ At least 8 characters";

    }


    // Uppercase

    if (/[A-Z]/.test(password)) {

        uppercase.textContent =
            "✓ One uppercase letter";

    } else {

        uppercase.textContent =
            "○ One uppercase letter";

    }


    // Number

    if (/[0-9]/.test(password)) {

        number.textContent =
            "✓ One number";

    } else {

        number.textContent =
            "○ One number";

    }


    // Special character

    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {

        special.textContent =
            "✓ One special character";

    } else {

        special.textContent =
            "○ One special character";

    }

});


// ===============================
// LOGIN
// ===============================

loginForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        // Clear previous message

        loginError.textContent = "";

        loginError.style.color = "";


        const email =
            emailInput.value.trim();

        const password =
            passwordInput.value;


        // ===============================
        // BASIC VALIDATION
        // ===============================

        if (!email) {

            loginError.textContent =
                "Please enter your email.";

            return;

        }


        if (!password) {

            loginError.textContent =
                "Please enter your password.";

            return;

        }


        // ===============================
        // LOGIN WITH SUPABASE
        // ===============================

        try {

            const {
                data,
                error
            } =
                await supabaseClient.auth
                    .signInWithPassword({

                        email: email,

                        password: password

                    });


            // ===============================
            // LOGIN ERROR
            // ===============================

            if (error) {

                console.error(
                    "Login error:",
                    error
                );


                if (
                    error.message
                        .toLowerCase()
                        .includes("email not confirmed")
                ) {

                    loginError.textContent =
                        "Please verify your email before logging in.";

                } else {

                    loginError.textContent =
                        "Invalid email or password.";

                }

                return;

            }


            // ===============================
            // LOGIN SUCCESS
            // ===============================

            if (data && data.user) {

                // Save login information

                localStorage.setItem(
                    "synaptichat_logged_in",
                    "true"
                );


                localStorage.setItem(
                    "synaptichat_email",
                    data.user.email
                );


                localStorage.setItem(
                    "synaptichat_user_id",
                    data.user.id
                );


                // Redirect to home page

                window.location.href =
                    "home.html";

            }

        } catch (error) {

            console.error(
                "Unexpected login error:",
                error
            );


            loginError.textContent =
                "Unable to connect to Supabase. Please try again.";

        }

    }
);


// ===============================
// FORGOT PASSWORD
// ===============================

document
    .getElementById("forgotPassword")
    .addEventListener(
        "click",
        async function (event) {

            event.preventDefault();


            const email =
                emailInput.value.trim();


            // ===============================
            // EMAIL REQUIRED
            // ===============================

            if (!email) {

                loginError.style.color = "";

                loginError.textContent =
                    "Please enter your email first.";

                return;

            }


            // ===============================
            // SEND RESET EMAIL
            // ===============================

            try {

                const {
                    error
                } =
                    await supabaseClient.auth
                        .resetPasswordForEmail(
                            email,
                            {
                                redirectTo:
                                    window.location.origin +
                                    "/reset-password.html"
                            }
                        );


                // ===============================
                // RESET ERROR
                // ===============================

                if (error) {

                    console.error(
                        "Password reset error:",
                        error
                    );


                    loginError.style.color = "";

                    loginError.textContent =
                        error.message;

                    return;

                }


                // ===============================
                // RESET SUCCESS
                // ===============================

                loginError.style.color =
                    "#86efac";


                loginError.textContent =
                    "Password reset link sent! Please check your email.";

            } catch (error) {

                console.error(
                    "Password reset error:",
                    error
                );


                loginError.style.color = "";

                loginError.textContent =
                    "Unable to send password reset email.";

            }

        }
    );