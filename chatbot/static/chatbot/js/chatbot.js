document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.querySelector(".chat-box");
    const chatInput = document.querySelector(".chat-input");
    const sendBtn = document.querySelector(".send-btn");
    const createDiaryBtn = document.querySelector(".create-diary-btn");
    
    let sessionId = chatBox.dataset.sessionId || null;
  
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
  
    // 말풍선을 DOM에 추가하는 헬퍼 함수
    function addChatBubble(text, side) {
      const bubble = document.createElement("div");
      bubble.classList.add("chat-bubble", side); // left 또는 right
      bubble.textContent = text;
      chatBox.appendChild(bubble);
      
      // 채팅 박스를 항상 아래로 스크롤
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  });
  