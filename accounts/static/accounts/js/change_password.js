document.addEventListener("DOMContentLoaded", function () {
    const userId = sessionStorage.getItem("user_id");
    const passwordForm = document.querySelector(".password-form");

    passwordForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const oldPassword = e.target.oldpassword.value;
        const newPassword = e.target.newpassword.value;

        try {
            const response = await axios.put(`/accounts/api/profile/${userId}/change-password/`, {
                old_password: oldPassword,
                new_password: newPassword
            });

            window.location.href = "/diary/";
        } catch (error) {
            return;
        }
    });
});