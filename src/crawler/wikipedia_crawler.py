# File: src/crawler/wikipedia_crawler.py
"""
Wikipedia 크롤러 - 고양이 관련 지식 수집
"""
import wikipediaapi
import json
from typing import List, Dict
from pathlib import Path
import time


class WikipediaCrawler:
    """위키피디아에서 고양이 관련 지식 크롤링"""
    
    def __init__(self, language: str = "ko"):
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent='GDPP-AI-Docent/1.0 (Educational Project)'
        )
        
    def get_page_content(self, page_title: str) -> Dict:
        """특정 페이지의 내용 가져오기"""
        page = self.wiki.page(page_title)
        
        if not page.exists():
            print(f"[WARNING] 페이지가 존재하지 않습니다: {page_title}")
            return None
            
        return {
            "title": page.title,
            "summary": page.summary,
            "text": page.text,
            "url": page.fullurl,
            "categories": [cat.title for cat in page.categories.values()]
        }
    
    def crawl_cat_knowledge(self) -> List[Dict]:
        """고양이 관련 주요 페이지 크롤링"""
        
        # 크롤링할 주요 페이지 목록
        cat_pages = [
            "고양이",
            "고양이의 행동",
            "고양이 품종",
            "페르시안 고양이",
            "샴 고양이",
            "러시안 블루",
            "메인쿤",
            "브리티시 쇼트헤어",
            "스코티시 폴드",
            "벵골 고양이",
            "고양이 사료",
            "고양이 건강",
            "고양이 영양",
            "반려동물",
            "고양이 훈련",
            "고양이 털",
            "고양이 발톱",
            "캣닢",
            "고양이 모래",
            "고양이 장난감"
        ]
        
        all_data = []
        
        print(f"[INFO] 위키피디아 크롤링 시작 ({len(cat_pages)}개 페이지)")
        
        for i, page_title in enumerate(cat_pages, 1):
            print(f"  [{i}/{len(cat_pages)}] {page_title} 크롤링 중...")
            
            page_data = self.get_page_content(page_title)
            
            if page_data:
                all_data.append(page_data)
                print(f"    [OK] 완료 (텍스트 길이: {len(page_data['text'])} 자)")
            
            # 서버 부하 방지를 위한 딜레이
            time.sleep(0.5)
        
        print(f"\n[SUCCESS] 총 {len(all_data)}개 페이지 크롤링 완료")
        return all_data
    
    def save_to_json(self, data: List[Dict], filepath: str):
        """데이터를 JSON 파일로 저장"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVED] 데이터 저장 완료: {filepath}")


if __name__ == "__main__":
    # 크롤러 실행
    crawler = WikipediaCrawler(language="ko")
    
    # 고양이 지식 크롤링
    cat_data = crawler.crawl_cat_knowledge()
    
    # 저장
    crawler.save_to_json(cat_data, "data/raw/wikipedia_cat_knowledge.json")
    
    # 통계 출력
    total_chars = sum(len(page['text']) for page in cat_data)
    print(f"\n[STATS] 통계:")
    print(f"  - 총 페이지 수: {len(cat_data)}")
    print(f"  - 총 텍스트 길이: {total_chars:,} 자")
    print(f"  - 평균 페이지 길이: {total_chars // len(cat_data):,} 자")
