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
        currentPath === "/" ||
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
    const loginLogoutLink = document.getElementById('login-logout-link');
    const signupProfileLink = document.getElementById('signup-profile-link');

    axios.get('/accounts/userinfo/')
        .then(response => {
            loginLogoutLink.textContent = '로그아웃';
            loginLogoutLink.style.cursor = 'pointer';
            loginLogoutLink.addEventListener('click', function (e) {
                e.preventDefault();
                logout();
            });
            signupProfileLink.textContent = '프로필';
            signupProfileLink.style.cursor = 'pointer';
            signupProfileLink.addEventListener('click', function() {
              window.location.href = "/diary/";
            });
        })
        .catch(error => {
            loginLogoutLink.textContent = '로그인';
            loginLogoutLink.style.cursor = 'pointer';
            loginLogoutLink.addEventListener('click', function() {
                window.location.href = "/accounts/login/";
            });
            signupProfileLink.textContent = '회원가입';
            signupProfileLink.style.cursor = 'pointer';
            signupProfileLink.addEventListener('click', function() {
                window.location.href = "/accounts/signup/";
            });
        });
});

function logout() {
    axios.post('/accounts/logout/')
        .then(response => {
            window.location.href = "/";
        })
        .catch(error => {
          return;
        });
}