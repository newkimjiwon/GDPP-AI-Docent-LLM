# File: src/model/prompt_template.py
"""
프롬프트 템플릿 및 컨텍스트 주입
"""
from typing import List, Dict


class PromptTemplate:
    """프롬프트 템플릿 관리"""
    
    SYSTEM_PROMPT = """당신은 궁디팡팡 캣페스타의 전문 AI 도슨트입니다.
방문객들에게 브랜드 정보, 제품 추천, 부스 위치 등을 친절하게 안내합니다.

중요한 규칙:
1. 제공된 [Context]에 있는 정보만 사용하세요. Context에 없는 정보는 절대 만들어내지 마세요.
2. 정보가 없으면 "죄송하지만 해당 정보가 없습니다"라고 정확히 답하세요.
3. 부스 번호, 브랜드명 등 구체적인 정보는 반드시 Context에서 확인 후 답변하세요.
4. 이전 답변이 틀렸다면 솔직히 인정하고 Context 기반으로 정정하세요.
5. 친절하고 명확하게 답변하세요.
6. 한국어로만 답변하세요.
7. 브랜드 정보를 제공할 때는 부스 위치도 함께 안내하세요.
8. "Context에서 확인한 바", "Context에 제공된" 등 Context를 반복적으로 언급하지 마세요. 자연스럽게 답변하세요.

절대 금지:
- Context에 없는 부스 번호나 브랜드 정보를 지어내는 것
- 불확실한 정보를 확신하는 듯이 답변하는 것
- 이전 답변과 모순되는 정보를 제공하는 것
- "Context에서", "Context에 따르면" 등의 표현을 반복적으로 사용하는 것"""

    @staticmethod
    def format_context(search_results: List[Dict]) -> str:
        """
        검색 결과를 컨텍스트 문자열로 포맷팅
        
        Args:
            search_results: 하이브리드 검색 결과 리스트
            
        Returns:
            포맷팅된 컨텍스트 문자열
        """
        if not search_results:
            return "관련 정보를 찾을 수 없습니다."
        
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            doc = result['document']
            metadata = result['metadata']
            source = metadata.get('source', 'unknown')
            
            # 브랜드 정보인 경우
            if source == 'gdpp_brand':
                brand_name = metadata.get('brand_name', '')
                category = metadata.get('category', '')
                booth = metadata.get('booth_location', '')
                
                context_parts.append(
                    f"[{i}] 브랜드: {brand_name}\n"
                    f"    카테고리: {category}\n"
                    f"    부스 위치: {booth}\n"
                    f"    정보: {doc}"
                )
            
            # Wikipedia 정보인 경우
            elif source == 'wikipedia':
                title = metadata.get('title', '')
                section = metadata.get('section', '')
                
                context_parts.append(
                    f"[{i}] 출처: Wikipedia - {title} ({section})\n"
                    f"    내용: {doc}"
                )
            
            # 기타
            else:
                context_parts.append(f"[{i}] {doc}")
        
        return "\n\n".join(context_parts)
    
    @staticmethod
    def create_prompt(query: str, context: str) -> str:
        """
        사용자 질문과 컨텍스트로 최종 프롬프트 생성
        
        Args:
            query: 사용자 질문
            context: 검색된 컨텍스트
            
        Returns:
            최종 프롬프트
        """
        return f"""[Context]
{context}

[User Question]
{query}

[Answer]
위의 Context를 참고하여 User Question에 답변해주세요. Context에 없는 정보는 절대 지어내지 마세요."""


def create_chat_prompt(query: str, search_results: List[Dict]) -> Dict[str, str]:
    """
    채팅 형식의 프롬프트 생성
    
    Args:
        query: 사용자 질문
        search_results: 검색 결과 리스트
        
    Returns:
        {"system": "...", "prompt": "..."}
    """
    context = PromptTemplate.format_context(search_results)
    prompt = PromptTemplate.create_prompt(query, context)
    
    return {
        "system": PromptTemplate.SYSTEM_PROMPT,
        "prompt": prompt
    }


if __name__ == "__main__":
    # 테스트
    sample_results = [
        {
            "document": "브랜드명: 건강백서캣\n카테고리: 헬스케어\n설명: 고양이 건강 관리 전문 브랜드. 건강 보조제 및 기능성 제품 제공.\n주요 제품: 건강 보조제, 영양제, 기능성 간식\n부스 위치: A구역",
            "metadata": {
                "source": "gdpp_brand",
                "brand_name": "건강백서캣",
                "category": "헬스케어",
                "booth_location": "A구역"
            },
            "hybrid_score": 0.85
        },
        {
            "document": "고양이(학명: Felis catus)는 식육목 고양이과에 속하는 포유류이다. 집고양이의 기원은 약 1만년 전 중동 지역에서 시작되었다.",
            "metadata": {
                "source": "wikipedia",
                "title": "고양이",
                "section": "서론"
            },
            "hybrid_score": 0.72
        }
    ]
    
    # 컨텍스트 포맷팅 테스트
    print("[TEST] 컨텍스트 포맷팅")
    print("=" * 60)
    context = PromptTemplate.format_context(sample_results)
    print(context)
    
    # 프롬프트 생성 테스트
    print("\n\n[TEST] 최종 프롬프트 생성")
    print("=" * 60)
    query = "건강백서캣에 대해 알려주세요"
    prompt_data = create_chat_prompt(query, sample_results)
    
    print("[SYSTEM]")
    print(prompt_data['system'])
    print("\n[PROMPT]")
    print(prompt_data['prompt'])
