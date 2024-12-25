FROM python:3.10.14

# 작업 디렉토리
WORKDIR /app

# 필수 패키지 설치
COPY requirements.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 (포트가 있어야 접근 가능)
EXPOSE 8000

# Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]