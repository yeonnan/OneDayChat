document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.querySelector(".start-btn");

    startBtn.addEventListener('click', function (e) {
        e.preventDefault();

        axios.get('/accounts/userinfo/')
            .then(response => {
                window.location.href = "/chatbot/";
            })
            .catch(error => {
                window.location.href = "/accounts/login/";
            });
    });
});