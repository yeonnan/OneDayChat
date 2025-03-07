axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { config, response } = error;
      
      // 1) 401이 아니면 그냥 에러 반환
      if (!response || response.status !== 401) {
        return Promise.reject(error);
      }
      
      // 2) 이미 재시도 했다면 그마저도 중단
      if (config && config.__isRetry) {
        // 재시도 후에도 401이면 더 이상은 무한루프 방지
        return Promise.reject(error);
      }
  
      // 3) 현재 경로 확인
      const currentPath = window.location.pathname;
      if (
        currentPath === "/main/" ||
        currentPath === "/accounts/login/" ||
        currentPath === "/accounts/signup/"
      ) {
        return Promise.reject(error);
      }
  
      // 4) 나머지 경우엔 refresh 시도
      config.__isRetry = true;
      try {
        await axios.post('/accounts/token/refresh/');
        return axios(config); // 재요청
      } catch (refreshError) {
        logout();
        window.location.href = '/accounts/login/';
        return Promise.reject(refreshError);
      }
    }
  );
  


document.addEventListener('DOMContentLoaded', () => {
    const deleteBtn = document.getElementById('delete-btn');
    const loginLogoutLink = document.getElementById('login-logout-link');
    const signupProfileLink = document.getElementById('signup-profile-link');

    axios.get('/accounts/userinfo/')
        .then(response => {
            const userId = sessionStorage.getItem("user_id");
            deleteBtn.textContent = '회원 탈퇴';
            deleteBtn.style.cursor = 'pointer';
            deleteBtn.addEventListener('click', function() {
              window.location.href = `/accounts/profile/${userId}/delete`;
            })
            loginLogoutLink.textContent = '로그아웃';
            loginLogoutLink.style.cursor = 'pointer';
            loginLogoutLink.addEventListener('click', function (e) {
                e.preventDefault();
                logout();
            });
            signupProfileLink.textContent = '비밀번호 변경';
            signupProfileLink.style.cursor = 'pointer';
            signupProfileLink.addEventListener('click', function() {
              window.location.href = `/accounts/profile/${userId}/change-password/`;
            })
            axios.get('/diary/api/')
                .then(res => {
                    const diaries = res.data
                    displayDiary(diaries);
                })
                .catch(err => {
                    return;
                })
        })
        .catch(error => {
            window.location.href = '/accounts/login/';
            });
        });

function logout() {
    axios.post('/accounts/logout/')
        .then(response => {
            window.location.href = "/main/";
        })
        .catch(error => {
            return;
        });
}

function displayDiary(diaries) {
  const diaryGrid = document.querySelector('.diary-grid');
  diaryGrid.innerHTML = '';

  diaries.forEach(diary => {
      // diary item을 감싸는 div 생성
      const diaryElement = document.createElement('div');
      diaryElement.classList.add('diary-item');

      // 날짜 표시 (YYYY.MM.DD 형태)
      const dateText = diary.created_at.substring(0, 10).replace(/-/g, ".");
      diaryElement.textContent = dateText;

      // CSS로 포인터로 표시(마우스 올리면 손가락 커서)
      diaryElement.style.cursor = 'pointer';

      // 클릭하면 /diary/<diary.id>/ 로 이동
      diaryElement.addEventListener('click', function() {
          window.location.href = `/diary/${diary.id}/`;
      });

      // .diary-grid 내부에 삽입
      diaryGrid.appendChild(diaryElement);
  });
}
