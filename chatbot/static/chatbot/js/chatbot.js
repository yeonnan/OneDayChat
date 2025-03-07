document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.querySelector(".chat-box");
    const chatInput = document.querySelector(".chat-input");
    const sendBtn = document.querySelector(".send-btn");
    const plusBtn = document.querySelector(".plus-btn");
    const fileInput = document.querySelector(".file-input");
    const createDiaryBtn = document.querySelector(".create-diary-btn");
    
    let sessionId = chatBox.dataset.sessionId || null;

    // "+" 버튼 클릭 -> 숨긴 file input
    plusBtn.addEventListener("click", function() {
      fileInput.click();
    });

    // 이미지 선택시 업로드 처리
    fileInput.addEventListener("change", async function() {
      if (fileInput.files && fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];

        try {
          const formData = new FormData();
          formData.append("image", selectedFile);

          // 서버에 이미지 업로드 (chatbot/upload-image/ 경로로 POST)
          const response = await axios.post("/chatbot/upload-image/", formData, {
            headers: {
              "Content-Type": "multipart/form-data"
            }
          });

          // 백엔드에서 응답받은 이미지 URL
          const imageUrl = response.data.image_url;
          
          // 채팅 말풍선(오른쪽)으로 이미지 표시
          addImageBubble(imageUrl, "right");

          // 만약 업로드한 이미지를 ChatBot 모델에 저장
          await axios.post("/chatbot/api/", { 
            message: "[이미지 업로드]", 
            image_url: imageUrl 
          });

        } catch (error) {
          console.error("이미지 업로드 에러:", error);
          addChatBubble("이미지 업로드 실패!", "left");
        } finally {
          // 같은 파일을 다시 선택할 수 있도록 초기화
          fileInput.value = "";
        }
      }
    });


  
    // "전송" 버튼을 눌렀을 때 이벤트
    sendBtn.addEventListener("click", async function() {
      const userMessage = chatInput.value.trim();
      if (!userMessage) return; // 빈 입력이면 무시
  
      // 사용자의 메시지를 먼저 화면에 표시 (오른쪽 말풍선)
      addChatBubble(userMessage, "right");
      
      try {
        // 서버에 메시지 전송
        const response = await axios.post("/chatbot/api/", { message: userMessage });
        
        // AI 응답 텍스트 추출
        const aiResponse = response.data.response; 
        
        // AI 응답 화면 표시 (왼쪽 말풍선)
        addChatBubble(aiResponse, "left");

        if (response.data.session_id) {
          sessionId = response.data.session_id;
          chatBox.dataset.sessionId = sessionId;
        }
        
      } catch (error) {

        // 필요하면 에러 표시 말풍선 추가 가능
        addChatBubble("에러가 발생했습니다.", "left");
      } finally {
        // 입력창 비우기
        chatInput.value = "";
        // 포커스 다시 입력창으로
        chatInput.focus();
      }
    });
  
    // "일기 생성" 버튼 클릭 시 페이지 이동
    createDiaryBtn.addEventListener("click", async function() {
        if (!sessionId) {
          alert("먼저 채팅을 입력하세요!");
          return;
        }
        try {
            const response = await axios.post(`/chatbot/create-diary/${sessionId}/`);
            const diaryId = response.data.diary_id;
            window.location.href = `/diary/${diaryId}`;
        } catch (error) {
          return;
        }
    });
  
    // 말풍선을 DOM에 추가
    function addChatBubble(text, side) {
      const bubble = document.createElement("div");
      bubble.classList.add("chat-bubble", side); 
      bubble.textContent = text;
      chatBox.appendChild(bubble);
      
      // 채팅 박스를 항상 아래로 스크롤
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 이미지 말풍선을 DOM에 추가
    function addImageBubble(imageSrc, side) {
      const bubble = document.createElement("div");
      bubble.classList.add("chat-bubble", side);

      const img = document.createElement("img");
      img.src = imageSrc;
      img.alt = "이미지 미리보기";
      img.style.maxWidth = "200px";  // 필요시 크기 조절
      bubble.appendChild(img);

      chatBox.appendChild(bubble);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
});