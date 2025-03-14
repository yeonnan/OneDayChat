# Project : One Day Chat
OpenAI API를 활용한 LLM 기반 대화형 일기 생성
챗봇과 대화를 통한 일기 생성 및 관리

## Development time
24.12 ~ 25.01 (현재 유지보수 및 업데이트 진행 중)

## Development Environment
- Programming Language : Python 3.10
- Framework : DJANGO, DRF
- Database : PostgreSQL
- Task Queue : Celery (자정마다 자동 일기 생성)
- Deployment : AWS EC2·S3, Docker-compose, Nginx, Ubuntu
- Version Control : Git, GitHub

## Installation
1. 깃허브 클론 및 디렉토리 이동
```
git clone https://github.com/yeonnan/OneDayChat.git
cd onedaychat
```

2. 환경 변수 파일 설정 (.env 생성 후 값 입력)


3. Docker 컨테이너 실행
```
docker compose build
docker compose up
```

4. Docker migration 진행
```
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

5. 서버 실행 확인
```
웹 브라우저에서 아래 주소에 접속하여 서버가 정상적으로 실행되는지 확인
http://localhost:8000 or http://<EC2 IP>:8000 
```

## API Documentation
https://yeonnan.hashnode.dev/one-day-chat-api-documentation

## ERD
![Image](https://github.com/user-attachments/assets/5851f92b-b35d-42f4-8663-eec88082d1fa)

