document.addEventListener("DOMContentLoaded", function() {
    const userId = sessionStorage.getItem("user_id");
    const deleteForm = document.querySelector(".delete-form");

    deleteForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const password = e.target.password.value;

        try {
            const response = await axios.delete(`/accounts/api/profile/${userId}/delete/`, {
                data: {
                    password: password
                }
            });
            window.location.href = "/main/";
        } catch (error) {
            return;
        }
    });
});