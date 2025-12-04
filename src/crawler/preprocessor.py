# File: src/crawler/preprocessor.py
"""
데이터 전처리 및 청킹 모듈
"""
import json
from typing import List, Dict, Tuple
from pathlib import Path
import re


class DataPreprocessor:
    """데이터 전처리 및 Semantic Chunking"""
    
    def __init__(self, max_chunk_length: int = 512):
        """
        Args:
            max_chunk_length: 최대 청크 길이 (토큰 수 기준)
        """
        self.max_chunk_length = max_chunk_length
    
    def clean_text(self, text: str) -> str:
        """텍스트 정제"""
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 특수 문자 정리 (필요한 경우)
        text = text.strip()
        
        return text
    
    def semantic_chunk_wikipedia(self, page_data: Dict) -> List[Dict]:
        """위키피디아 페이지를 의미 단위로 분할"""
        chunks = []
        
        title = page_data['title']
        text = page_data['text']
        
        # 섹션별로 분할 (== 섹션 제목 == 형식)
        sections = re.split(r'\n==\s*(.+?)\s*==\n', text)
        
        # 첫 번째 부분은 서론
        if sections[0].strip():
            chunks.append({
                "text": self.clean_text(sections[0]),
                "metadata": {
                    "source": "wikipedia",
                    "title": title,
                    "section": "서론",
                    "url": page_data['url']
                }
            })
        
        # 나머지 섹션 처리
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_title = sections[i].strip()
                section_text = sections[i + 1].strip()
                
                if section_text:
                    # 긴 섹션은 문단별로 추가 분할
                    if len(section_text) > self.max_chunk_length:
                        paragraphs = section_text.split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                chunks.append({
                                    "text": self.clean_text(para),
                                    "metadata": {
                                        "source": "wikipedia",
                                        "title": title,
                                        "section": section_title,
                                        "url": page_data['url']
                                    }
                                })
                    else:
                        chunks.append({
                            "text": self.clean_text(section_text),
                            "metadata": {
                                "source": "wikipedia",
                                "title": title,
                                "section": section_title,
                                "url": page_data['url']
                            }
                        })
        
        return chunks
    
    def chunk_brand_data(self, brand: Dict) -> Dict:
        """브랜드 데이터를 청크로 변환"""
        # 검색용 텍스트 (간결하게 유지)
        text_parts = [
            f"브랜드명: {brand['brand_name']}",
            f"카테고리: {brand['category']}",
            f"설명: {brand['description']}"
        ]
        
        # 부스 번호 추가
        if brand.get('booth_number'):
            text_parts.append(f"부스 번호: {brand['booth_number']}")
        
        # 홈페이지 추가
        if brand.get('homepage'):
            text_parts.append(f"홈페이지: {brand['homepage']}")
        
        # 인스타그램 추가
        if brand.get('instagram'):
            text_parts.append(f"인스타그램: {brand['instagram']}")
        
        # 태그 추가 (검색 향상)
        if brand.get('tags'):
            text_parts.append(f"태그: {brand['tags']}")
        
        text = '\n'.join(text_parts)
        
        return {
            "text": text,
            "metadata": {
                "source": "gdpp_brand",
                # 원본 브랜드 데이터 전체를 메타데이터에 저장 (None 방지)
                "brand_name": brand.get('brand_name') or '',
                "booth_number": brand.get('booth_number') or '',
                "category": brand.get('category') or '',
                "master_category": brand.get('master_category') or '',
                "description": brand.get('description') or '',
                "homepage": brand.get('homepage') or '',
                "instagram": brand.get('instagram') or '',
                "tags": brand.get('tags') or '',
                "all_categories": brand.get('all_categories') or '',
                "url": brand.get('source_url') or '',
                # 이미지는 제외 (용량 절약)
            }
        }
    
    def process_wikipedia_data(self, input_file: str) -> List[Dict]:
        """위키피디아 데이터 전처리"""
        print(f"[INFO] 위키피디아 데이터 처리 중: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            pages = json.load(f)
        
        all_chunks = []
        for page in pages:
            chunks = self.semantic_chunk_wikipedia(page)
            all_chunks.extend(chunks)
        
        print(f"  [OK] {len(pages)}개 페이지 -> {len(all_chunks)}개 청크")
        return all_chunks
    
    def process_brand_data(self, input_file: str) -> List[Dict]:
        """브랜드 데이터 전처리"""
        print(f"[INFO] 브랜드 데이터 처리 중: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            brands = json.load(f)
        
        chunks = [self.chunk_brand_data(brand) for brand in brands]
        
        print(f"  [OK] {len(brands)}개 브랜드 -> {len(chunks)}개 청크")
        return chunks
    
    def chunk_faq_data(self, faq: Dict) -> Dict:
        """FAQ 데이터를 청크로 변환"""
        text = f"질문: {faq['question']}\n답변: {faq['answer']}"
        
        return {
            "text": text,
            "metadata": {
                "source": "gdpp_faq",
                "category": faq.get('category', 'general'),
                "url": faq.get('source_url', '')
            }
        }
    
    def chunk_event_info(self, event_info: Dict) -> List[Dict]:
        """이벤트 정보를 청크로 변환"""
        chunks = []
        
        # 사무국 정보
        contact = event_info.get('contact', {})
        contact_text = f"""궁디팡팡 캣페스타 운영 사무국
운영 시간: {contact.get('office_hours', '')}
이메일: {contact.get('email', '')}
전화: {contact.get('phone', '')}
문의하기: {contact.get('inquiry_page', '')}
공식 홈페이지: {event_info.get('website', {}).get('main', '')}"""
        
        chunks.append({
            "text": contact_text,
            "metadata": {
                "source": "gdpp_event_info",
                "category": "contact",
                "url": event_info.get('website', {}).get('main', '')
            }
        })
        
        # 2025년 일정
        if 'schedule_2025' in event_info:
            schedule_text = "2025년 궁디팡팡 캣페스타 일정:\n"
            for event in event_info['schedule_2025']:
                schedule_text += f"제{event['event_number']}회: {event['dates']} / {event['location']}\n"
            
            chunks.append({
                "text": schedule_text,
                "metadata": {
                    "source": "gdpp_event_info",
                    "category": "schedule",
                    "url": event_info.get('website', {}).get('main', '')
                }
            })
        
        # 중요 규칙
        if 'important_rules' in event_info:
            rules = event_info['important_rules']
            rules_text = f"""궁디팡팡 캣페스타 중요 규칙:
반려동물 동반: {rules.get('pet_entry', '')}
재입장: {rules.get('re_entry', '')}
무료입장 대상: {', '.join(rules.get('free_entry_eligibility', []))}"""
            
            chunks.append({
                "text": rules_text,
                "metadata": {
                    "source": "gdpp_event_info",
                    "category": "rules",
                    "url": event_info.get('website', {}).get('main', '')
                }
            })
        
        return chunks
    
    def process_faq_data(self, input_file: str) -> List[Dict]:
        """FAQ 데이터 전처리"""
        print(f"[INFO] FAQ 데이터 처리 중: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            faqs = json.load(f)
        
        chunks = [self.chunk_faq_data(faq) for faq in faqs]
        
        print(f"  [OK] {len(faqs)}개 FAQ -> {len(chunks)}개 청크")
        return chunks
    
    def process_event_info(self, input_file: str) -> List[Dict]:
        """이벤트 정보 전처리"""
        print(f"[INFO] 이벤트 정보 처리 중: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
        
        all_chunks = []
        for event_info in event_data:
            chunks = self.chunk_event_info(event_info)
            all_chunks.extend(chunks)
        
        print(f"  [OK] {len(event_data)}개 이벤트 -> {len(all_chunks)}개 청크")
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], output_file: str):
        """청크 데이터 저장"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVED] 청크 데이터 저장 완료: {output_file}")
    
    def get_statistics(self, chunks: List[Dict]) -> Dict:
        """청크 통계 계산"""
        total_chars = sum(len(chunk['text']) for chunk in chunks)
        avg_chars = total_chars // len(chunks) if chunks else 0
        
        # 소스별 통계
        sources = {}
        for chunk in chunks:
            source = chunk['metadata']['source']
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_chunks": len(chunks),
            "total_chars": total_chars,
            "avg_chars": avg_chars,
            "sources": sources
        }


if __name__ == "__main__":
    preprocessor = DataPreprocessor(max_chunk_length=512)
    
    # 위키피디아 데이터 처리
    wiki_chunks = preprocessor.process_wikipedia_data("data/raw/wikipedia_cat_knowledge.json")
    
    # 브랜드 데이터 처리
    brand_chunks = preprocessor.process_brand_data("data/raw/gdpp_brands.json")
    
    # FAQ 데이터 처리
    faq_chunks = preprocessor.process_faq_data("data/raw/gdpp_faq.json")
    
    # 이벤트 정보 처리
    event_chunks = preprocessor.process_event_info("data/raw/gdpp_event_info.json")
    
    # 통합
    all_chunks = wiki_chunks + brand_chunks + faq_chunks + event_chunks
    
    # 저장
    preprocessor.save_chunks(all_chunks, "data/processed/all_chunks.json")
    
    # 통계 출력
    stats = preprocessor.get_statistics(all_chunks)
    print(f"\n[STATS] 전체 통계:")
    print(f"  - 총 청크 수: {stats['total_chunks']}")
    print(f"  - 총 텍스트 길이: {stats['total_chars']:,} 자")
    print(f"  - 평균 청크 길이: {stats['avg_chars']:,} 자")
    print(f"  - 소스별 분포:")
    for source, count in stats['sources'].items():
        print(f"    * {source}: {count}개")
