document.addEventListener("DOMContentLoaded", async function() {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const diaryId = pathParts[1];
    if (!diaryId) {
        return;
      }
    console.log("Current diaryId:", diaryId);

    const diaryDateSpan = document.querySelector(".diary-date");
    const diaryTextParagraph = document.querySelector(".diary-text");
    const editBtn = document.querySelector(".edit-btn");
    const deleteBtn = document.querySelector(".delete-btn");

    try {
        const response = await axios.get(`/diary/api/${diaryId}/`);
        const diaryData = response.data;

        if (diaryData.created_at) {
            const dateOnly = diaryData.created_at.substring(0, 10).replace(/-/g, ".");
            diaryDateSpan.textContent = dateOnly;
        }

        diaryTextParagraph.textContent = diaryData.content;
    } catch (error) {
        return;
    };

    editBtn.style.cursor = 'pointer';
    editBtn.addEventListener("click", function() {
        window.location.href = `/diary/${diaryId}/edit/`;
    })

    deleteBtn.style.cursor = 'pointer';
    deleteBtn.addEventListener("click", function (e) {
        e.preventDefault();
        diaryDel(diaryId);
    })
});

function diaryDel(diaryId) {
    axios.delete(`/diary/api/${diaryId}/`)
        .then(res => {
            window.location.href = "/diary/";
        })
        .catch(err => {
            return;
        });
}