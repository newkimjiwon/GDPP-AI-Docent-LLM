# File: src/crawler/faq_crawler.py
"""
GDPP FAQ 크롤러
"""
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
from pathlib import Path


class FAQCrawler:
    """FAQ 크롤러"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl_faq(self, url: str = "https://catfesta.com/information/visitor-faq/") -> List[Dict]:
        """FAQ 크롤링"""
        
        print(f"[INFO] FAQ 크롤링 시작: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # FAQ 항목 추출
            faqs = self.extract_faqs(soup)
            
            print(f"[SUCCESS] {len(faqs)}개의 FAQ 수집 완료")
            
            return faqs
            
        except Exception as e:
            print(f"[ERROR] 크롤링 실패: {e}")
            return []
    
    def extract_faqs(self, soup: BeautifulSoup) -> List[Dict]:
        """FAQ 항목 추출"""
        faqs = []
        
        # FAQ 항목 찾기 (h4 태그 with panel-title class)
        faq_headers = soup.find_all('h4', class_='panel-title')
        
        print(f"[INFO] {len(faq_headers)}개의 FAQ 헤더 발견")
        
        for header in faq_headers:
            try:
                # 질문 텍스트 추출
                question_link = header.find('a')
                if not question_link:
                    continue
                
                question = question_link.get_text(strip=True)
                
                # data-target 속성에서 답변 div ID 찾기
                target_id = question_link.get('data-target', '').replace('#', '')
                if not target_id:
                    continue
                
                # 답변 div 찾기
                answer_div = soup.find('div', id=target_id)
                if not answer_div:
                    continue
                
                # 답변 텍스트 추출
                answer = answer_div.get_text(strip=True)
                
                # 질문 텍스트가 답변에 포함되어 있으면 제거
                if answer.startswith(question):
                    answer = answer[len(question):].strip()
                
                if question and answer:
                    faqs.append({
                        "question": question,
                        "answer": answer,
                        "category": "visitor_faq",
                        "source_url": "https://catfesta.com/information/visitor-faq/"
                    })
                    
            except Exception as e:
                print(f"[WARNING] FAQ 항목 파싱 실패: {e}")
                continue
        
        return faqs
    
    def save_to_json(self, data: List[Dict], filepath: str):
        """JSON 파일로 저장"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVED] 데이터 저장 완료: {filepath}")


if __name__ == "__main__":
    crawler = FAQCrawler()
    
    # FAQ 크롤링
    faqs = crawler.crawl_faq()
    
    if faqs:
        crawler.save_to_json(faqs, "data/raw/gdpp_faq.json")
        
        # 통계 출력
        print(f"\n[STATS] 수집 통계:")
        print(f"  - 총 FAQ 수: {len(faqs)}")
        print(f"\n[SAMPLE] 첫 번째 FAQ:")
        print(f"  Q: {faqs[0]['question']}")
        print(f"  A: {faqs[0]['answer'][:100]}...")
    else:
        print("\n[ERROR] FAQ 데이터를 수집하지 못했습니다.")
