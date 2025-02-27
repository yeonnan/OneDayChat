document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.querySelector(".signup-form");

    signupForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const username = e.target.username.value;
        const email = e.target.email.value;
        const password = e.target.password.value;
        const nickname = e.target.nickname.value;

        try {
            const response = await axios.post("/accounts/api/signup/", {
                username: username,
                email: email,
                password: password,
                nickname: nickname
            });
            window.location.href = "/accounts/login/";
        } catch (err) {
            return;
        }
    });
});