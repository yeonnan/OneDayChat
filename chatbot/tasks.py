from celery import shared_task
from django.utils import timezone
from .models import ChatSession, ChatBot
from diary.models import Diary
from .openai_service import create_diary

@shared_task
def create_daily_diaries():
    # 1. 오늘 날짜
    today = timezone.localdate()
    
    # 2. 오늘 만든 ChatSession 중에서 Diary가 없는 세션 찾기
    sessions = ChatSession.objects.filter(created_at__date=today)
    
    for session in sessions:
        user = session.user

        # 1) diary가 있는지 확인
        existing_diary = Diary.objects.filter(session=session).first()

        # 2) 대화 메세지(요약 제외) 불러오기
        chat_messages = ChatBot.objects.filter(session=session).exclude(
            message_text__startswith="[대화 요약]"
        ).order_by("timestamp")

        if not chat_messages.exists():
            continue
        
        # 3) openai로 일기 작성
        try:
            new_diary_content = create_diary(chat_history=chat_messages, user=user)
        except Exception as e:
            print(f"Error creating diary for session {session.id}: {e}")
            continue

        # 4) diary가 있으면 업데이트, 없으면 생성
        session_date = session.created_at.date()
        if existing_diary:
            existing_diary.content = new_diary_content
            existing_diary.updated_at = timezone.now()  # 수정 시간 갱신
            existing_diary.save()
            print(f"일기를 업데이트했습니다. (session={session.id})")
        else:
            Diary.objects.create(
                user=user,
                session=session,
                title=str(session_date),
                content=new_diary_content,
            )
            print(f"일기를 생성했습니다. (session={session.id})")

    return "자동 일기 생성 작업 완료"
