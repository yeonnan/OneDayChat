import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# 요약 llm
def summarize_chat_history(chat_history, user):
    summary_messages = [
        {
            "role": "system",
            "content": ("너는 대화 내용을 요약하는 비서야. 대화의 핵심 내용을 간결하고 명확하게 정리해" "간단한 인사말('안녕', '잘지냈어?')은 제외하고 주요 질문과 답변만 요약해"),
        }
    ]
    for msg in chat_history:
        if msg.user == user:
            role = "user"
        else:
            role = "assistant"
        summary_messages.append({"role": role, "content": msg.message_text})

    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=summary_messages)
    return completion.choices[0].message.content


# 챗봇 llm
def chatbot_response(chat_history, user_message, user):
    messages = [
        {
            "role": "system",
            "content": (
                "너는 사용자의 친근한 대화 상대야. 사용자가 하루 일과나 감정을 말하면 공감하며 반응해. "
                "이전 대화를 기억하고 그에 맞는 응답을 하며, 공손하지만 친근한 반말로 답변해."
            ),
        }
    ]

    # 이전 대화 기록을 메세지 포멧에 맞게 변환
    for msg in chat_history:
        if msg.user == user:
            role = "user"
        else:
            role = "assistant"
        messages.append({"role": role, "content": msg.message_text})

    # 사용자 메세지 추가
    messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(model="gpt-4o", messages=messages)
    return completion.choices[0].message.content


# 다이어리 생성 llm
def create_diary(chat_history, user):
    messages = [
        {
            "role": "system",
            "content": (
                "너는 세션에 있는 대화 내용을 바탕으로 일기를 작성하는 비서야."
                "다른 감정과 불필요한 말은 추가하지 말고 사용자가 대화한 내용을 기반으로 일기를 작성해"
                "인칭이 필요하다면 1인칭으로 유저가 작성한 것이라 생각하고 작성해"
            ),
        }
    ]

    for msg in chat_history:
        if msg.user == user:
            role = "user"
        else:
            role = "assistant"
        messages.append({"role": role, "content": msg.message_text})

    completion = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.7)
    return completion.choices[0].message.content
