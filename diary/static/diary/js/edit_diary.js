document.addEventListener("DOMContentLoaded", async function() {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const diaryId = pathParts[1];
    if (!diaryId) return;
  
    const diaryDateSpan   = document.querySelector(".diary-date");
    const diaryTextarea   = document.querySelector(".content-textarea");
    const editSubmitBtn   = document.querySelector(".edit-submit-btn");
    const imagesContainer = document.querySelector(".diary-images-container");
  
    // 1) 다이어리 상세 불러오기
    let diaryData;
    try {
      const response = await axios.get(`/diary/api/${diaryId}/`);
      diaryData = response.data;
  
      // 날짜 표기
      if (diaryData.create_at) {
        diaryDateSpan.textContent = diaryData.create_at.substring(0, 10).replace(/-/g, '.');
      }
      // 본문
      if (diaryData.content) {
        diaryTextarea.value = diaryData.content;
      }
  
      // 2) 이미지 표시 (Diary에 직접 연결된 이미지)
      if (diaryData.diary_image) {
        const { image_id, image_url } = diaryData.diary_image;
        renderImageItem(image_id, image_url, "DIARY"); 
      }
  
      // 3) 챗봇 중 업로드된 이미지들
      if (diaryData.chat_images && diaryData.chat_images.length > 0) {
        diaryData.chat_images.forEach(imgObj => {
          renderImageItem(imgObj.image_id, imgObj.image_url, "CHATBOT");
        });
      }
  
    } catch (error) {
      console.error("일기 조회 에러:", error);
      return;
    }
  
    // 4) "수정완료" 버튼
    editSubmitBtn.addEventListener("click", async function () {
      const newContent = diaryTextarea.value.trim();
      if (!newContent) return;
  
      try {
        await axios.put(`/diary/api/${diaryId}/`, {
          content: newContent
        });
        window.location.href = `/diary/${diaryId}/`;
      } catch (err) {
        console.error("일기 수정 에러:", err);
      }
    });
  
    // -------------------------------
    // 이미지를 화면에 렌더링하는 함수 (삭제 버튼 포함)
    function renderImageItem(imageId, imageUrl, imageType) {
      // imageType: "DIARY"면 Diary.image, "CHATBOT"이면 ChatBot의 이미지 등 구분용
      const wrapper = document.createElement("div");
      wrapper.classList.add("edit-image-wrapper");
  
      const imgEl = document.createElement("img");
      imgEl.src = imageUrl;
      imgEl.alt = "이미지 미리보기";
      imgEl.classList.add("edit-image");
      wrapper.appendChild(imgEl);
  
      // 삭제 버튼
      const delBtn = document.createElement("button");
      delBtn.textContent = "이미지 삭제";
      delBtn.classList.add("delete-image-btn");
      delBtn.addEventListener("click", async () => {
        if (!confirm("정말 이 이미지를 삭제하시겠습니까?")) return;
        try {
          // 백엔드로 삭제 요청
          // (RESTful하게 하려면 DELETE /diary/api/<diaryId>/image/<imageId> 형태 등)
          await axios.delete(`/diary/api/${diaryId}/image/`, {
            data: {
              image_id: imageId,
              image_type: imageType
            },
            headers: {
                "Content-Type": "application/json"
            }
          });
          // 삭제 성공 시 DOM에서도 제거
          wrapper.remove();
        } catch (err) {
          console.error("이미지 삭제 에러:", err);
        }
      });
      wrapper.appendChild(delBtn);
  
      imagesContainer.appendChild(wrapper);
    }
  });
  