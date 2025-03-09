document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector(".login-form");

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const username = e.target.username.value;
        const password = e.target.password.value;

        try {
            const response = await axios.post("/accounts/api/login/", {
                username: username,
                password: password
            });
            const userId = response.data.user_id;

            sessionStorage.setItem("user_id", userId);
            window.location.href = "/";
        } catch (err) {
            return;
        }
    });
    const signupButton = document.querySelector(".signup-btn");
    signupButton.addEventListener("click", function() {
        window.location.href = "/accounts/signup/";
    });
});