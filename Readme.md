# Project : One Day Chat
OpenAI API를 활용한 LLM 기반 대화형 일기 생성
챗봇과 대화를 통한 일기 생성 및 관리

## Development time
24.12 ~ 25.01

## Development Environment
- Programming Language : Python 3.10
- Framework : DJANGO, DRF
- Database : PostgreSQL
- Deployment : AWS EC2, Docker-compose, Nginx, Ubuntu
- Version Control : Git, GitHub

## Installation
1. 깃허브 클론
```
https://github.com/yeonnan/OneDayChat.git
```

2. python 패키지 설치
```
pip install -r requirements.txt
```
3. Django migration 진행
```
python manage.py makemigrations
python manage.py migrate
```

4. Django server 실행
```
python manage.py runserver
```


## API Documentation
https://yeonnan.hashnode.dev/one-day-chat-api-documentation

## ERD
![Image](https://github.com/user-attachments/assets/ecfe8efa-7c0a-4b0c-9bfe-195fcb0d736c)

