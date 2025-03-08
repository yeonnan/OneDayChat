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
        console.log("data: ", diaryData);

        // 1. 날짜 표시
        if (diaryData.created_at) {
            const dateOnly = diaryData.created_at.substring(0, 10).replace(/-/g, ".");
            diaryDateSpan.textContent = dateOnly;
        }
        
        // 2. 본문 표시
        diaryTextParagraph.textContent = diaryData.content;

        if (diaryData.diary_image) {
            const diaryContentDiv = document.querySelector(".diary-content");
            const { image_id, image_url } = diaryData.diary_image;
        
            const imgEl = document.createElement("img");
            imgEl.src = image_url;
            imgEl.alt = "다이어리에 첨부된 이미지";
            imgEl.classList.add("diary-image"); 
            diaryContentDiv.appendChild(imgEl);
        }
        
          // 4. 챗봇 대화 중 업로드된 이미지들
            if (diaryData.chat_images && diaryData.chat_images.length > 0) {
            const diaryContentDiv = document.querySelector(".diary-content");
            diaryData.chat_images.forEach(imgObj => {
                const imgEl = document.createElement("img");
                imgEl.src = imgObj.image_url;
                imgEl.alt = "대화 중 업로드된 이미지";
                imgEl.classList.add("diary-image");
                diaryContentDiv.appendChild(imgEl);
                });
            }
    } catch (error) {
        console.error("일기 상세 조회 에러:", error);
        return;
    }

    // 수정버튼
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
            console.error("일기 삭제 에러:", err);
        });
}