document.addEventListener("DOMContentLoaded", async function() {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const diaryId = pathParts[1];
    if (!diaryId) {
        return;
        }

    const diaryDateSpan = document.querySelector(".diary-date");
    const diaryTextarea = document.querySelector(".content-textarea");
    const editSubmitBtn = document.querySelector(".edit-submit-btn");

    try {
        const response = await axios.get(`/diary/api/${diaryId}/`);
        const diaryData = response.data;

        if (diaryData.create_at) {
            diaryDateSpan.textContent = diaryData.create_at.substring(0, 10).replace(/-/g, '.');
        };
        if (diaryData.content) {
            diaryTextarea.value = diaryData.content;
        };

    } catch (error) {
        return;
    };

    editSubmitBtn.addEventListener("click", async function () {
        const newContent = diaryTextarea.value;
        if (!newContent.trim()) {
            return;
        };

        try {
            const putResponse = await axios.put(`/diary/api/${diaryId}/`, {
                content: newContent
            });
            window.location.href = `/diary/${diaryId}/`;
        } catch (err) {
            return;
        };
    });
});