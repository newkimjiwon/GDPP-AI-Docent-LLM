# File: app/streamlit_app.py
"""
GDPP AI Docent - Streamlit 챗봇 UI
"""
import streamlit as st
import requests
import json
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 페이지 설정
st.set_page_config(
    page_title="궁디팡팡 AI 도슨트",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 20%;
    }
    .source-box {
        background-color: #FFF9C4;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# API 설정
API_BASE_URL = "http://localhost:8000/api"

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_available" not in st.session_state:
    st.session_state.api_available = False


def check_api_status():
    """API 서버 상태 확인"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None


def send_message(message: str, temperature: float = 0.7, top_k: int = 5):
    """메시지 전송"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "temperature": temperature,
                "top_k": top_k
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"[ERROR] API 호출 실패: {response.status_code}", "sources": []}
    except Exception as e:
        return {"response": f"[ERROR] {str(e)}", "sources": []}


# 헤더
st.markdown('<div class="main-header">🐱 궁디팡팡 AI 도슨트</div>', unsafe_allow_html=True)
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 상태 확인
    if st.button("API 상태 확인"):
        is_available, status_data = check_api_status()
        st.session_state.api_available = is_available
        
        if is_available:
            st.success("API 서버 연결됨")
            
            # 상태 정보 표시
            if status_data:
                st.json(status_data)
        else:
            st.error("API 서버에 연결할 수 없습니다")
            st.info("백엔드 서버를 시작하세요:\n```bash\ncd /mnt/d/Project/GDDPAIDocent\npython -m uvicorn src.api.main:app --reload\n```")
    
    st.markdown("---")
    
    # 파라미터 설정
    st.subheader("파라미터")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    top_k = st.slider("검색 결과 수 (Top K)", 1, 10, 5, 1)
    
    st.markdown("---")
    
    # 대화 초기화
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # 정보
    st.subheader("정보")
    st.markdown("""
    **궁디팡팡 AI 도슨트**는 캣페스타 방문객을 위한 AI 안내 챗봇입니다.
    
    **기능:**
    - 브랜드 정보 검색
    - 제품 추천
    - 부스 위치 안내
    - 고양이 관련 지식 제공
    
    **사용 예시:**
    - "고양이 사료 추천해줘"
    - "건강백서캣에 대해 알려줘"
    - "고양이 품종은 어떤 것들이 있나요?"
    """)

# 메인 영역
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 대화")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f'<div class="chat-message user-message">👤 **사용자**: {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 **AI 도슨트**: {content}</div>', unsafe_allow_html=True)
                
                # 소스 정보 표시
                if "sources" in message and message["sources"]:
                    sources_text = "**참고 자료:**\n"
                    for i, source in enumerate(message["sources"], 1):
                        sources_text += f"{i}. {source.get('title', 'Unknown')} (출처: {source.get('source', 'Unknown')})\n"
                    
                    st.markdown(f'<div class="source-box">{sources_text}</div>', unsafe_allow_html=True)
    
    # 입력 영역
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "메시지를 입력하세요...",
            key="user_input",
            placeholder="예: 고양이 사료 추천해줘"
        )
        
        submit_button = st.form_submit_button("전송")
    
    if submit_button and user_input:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # API 호출
        with st.spinner("AI 도슨트가 답변을 생성하고 있습니다..."):
            response_data = send_message(user_input, temperature, top_k)
        
        # AI 응답 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data.get("response", "응답을 생성할 수 없습니다."),
            "sources": response_data.get("sources", [])
        })
        
        # 페이지 새로고침
        st.rerun()

with col2:
    st.subheader("통계")
    
    # 대화 통계
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    st.metric("전체 메시지", total_messages)
    st.metric("사용자 질문", user_messages)
    
    st.markdown("---")
    
    # 추천 질문
    st.subheader("💡 추천 질문")
    
    sample_questions = [
        "고양이 사료 추천해줘",
        "건강백서캣에 대해 알려줘",
        "고양이 품종은 어떤 것들이 있나요?",
        "고양이 간식 브랜드 알려줘",
        "고양이 모래 추천해줘"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{question}"):
            # 질문 자동 입력
            st.session_state.messages.append({
                "role": "user",
                "content": question
            })
            
            # API 호출
            with st.spinner("AI 도슨트가 답변을 생성하고 있습니다..."):
                response_data = send_message(question, temperature, top_k)
            
            # AI 응답 추가
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data.get("response", "응답을 생성할 수 없습니다."),
                "sources": response_data.get("sources", [])
            })
            
            st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray; font-size: 0.9rem;">'
    '© 2024 GDPP AI Docent | Powered by Local LLM + RAG'
    '</div>',
    unsafe_allow_html=True
)
