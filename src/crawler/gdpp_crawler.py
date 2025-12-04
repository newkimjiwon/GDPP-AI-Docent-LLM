# File: src/crawler/gdpp_crawler.py
"""
GDPP 브랜드 크롤러 - JavaScript에서 데이터 추출
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict
from pathlib import Path


class GDPPBrandCrawler:
    """GDPP 브랜드 크롤러"""
    
    def __init__(self):
        """
        크롤러 초기화
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
            
    def crawl_brands(self, url: str = "https://gdppcat.com/brand") -> List[Dict]:
        """브랜드 정보 크롤링"""
        
        print(f"[INFO] 크롤링 시작: {url}")
        
        try:
            # HTTP 요청
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 브랜드 데이터 추출
            brands = self.extract_brands(soup)
            
            print(f"[SUCCESS] {len(brands)}개의 브랜드 데이터 수집 완료")
            
            return brands
            
        except Exception as e:
            print(f"[ERROR] 크롤링 실패: {e}")
            return []
    

    
    def extract_brands(self, soup: BeautifulSoup) -> List[Dict]:
        """JavaScript에서 브랜드 데이터 추출"""
        brands = []
        
        # script 태그에서 brand_list 찾기
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'brand_list:' in script.string:
                try:
                    # brand_list: 위치 찾기
                    start_idx = script.string.find('brand_list:')
                    if start_idx == -1:
                        continue
                    
                    # 배열 시작 위치 찾기
                    array_start = script.string.find('[', start_idx)
                    if array_start == -1:
                        continue
                    
                    # 괄호 카운팅으로 배열 끝 찾기
                    bracket_count = 0
                    in_string = False
                    escape_next = False
                    array_end = -1
                    
                    for j, char in enumerate(script.string[array_start:], start=array_start):
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not escape_next:
                            in_string = not in_string
                        
                        if not in_string:
                            if char == '[':
                                bracket_count += 1
                            elif char == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    array_end = j + 1
                                    break
                    
                    if array_end == -1:
                        print("[ERROR] 배열 끝을 찾을 수 없습니다.")
                        continue
                    
                    # JSON 파싱
                    json_str = script.string[array_start:array_end]
                    brand_data = json.loads(json_str)
                    
                    print(f"[INFO] JavaScript에서 {len(brand_data)}개의 브랜드 데이터 발견")
                    
                    # 각 브랜드 데이터 파싱
                    for brand_obj in brand_data:
                        brand_info = self.parse_brand_element(brand_obj)
                        if brand_info:
                            brands.append(brand_info)
                    
                    break  # 데이터를 찾았으면 종료
                    
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 파싱 실패: {e}")
                    continue
                except Exception as e:
                    print(f"[ERROR] 데이터 추출 실패: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        if not brands:
            print("[WARNING] 브랜드 데이터를 찾지 못했습니다.")
        
        return brands
    
    def parse_brand_element(self, brand_obj: Dict) -> Dict:
        """JSON 객체에서 브랜드 정보 추출"""
        
        try:
            return {
                # 기본 정보
                "brand_name": brand_obj.get("PR_NAME_KR", ""),
                "booth_number": brand_obj.get("BOOTH_NUMBER", ""),
                "category": brand_obj.get("CATEGORY_DESC", ""),
                "master_category": brand_obj.get("MASTER_CATEGORY_DESC", ""),
                "description": brand_obj.get("COMPANY_INFO", ""),
                
                # 연락처 정보
                "homepage": brand_obj.get("HOMEPAGE", ""),
                "instagram": brand_obj.get("INSTAGRAM_ACCOUNT", ""),
                
                # 이미지 URL들
                "image_url_1": brand_obj.get("IMG_URL_1", ""),
                "image_url_2": brand_obj.get("IMG_URL_2", ""),
                "image_url_3": brand_obj.get("IMG_URL_3", ""),
                "image_thumb_url_1": brand_obj.get("IMG_THUMB_URL_1", ""),
                "image_thumb_url_2": brand_obj.get("IMG_THUMB_URL_2", ""),
                "image_thumb_url_3": brand_obj.get("IMG_THUMB_URL_3", ""),
                
                # 추가 정보
                "tags": brand_obj.get("TAG", ""),
                "all_categories": brand_obj.get("CATEGORY_DESCs", ""),
                
                # 메타 정보
                "source_url": "https://gdppcat.com/brand",
                "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"[ERROR] 브랜드 데이터 파싱 실패: {e}")
            return None
    
    def save_to_json(self, data: List[Dict], filepath: str):
        """ JSON  """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"   : {filepath}")


if __name__ == "__main__":
    # 크롤러 실행
    crawler = GDPPBrandCrawler()    
    
    #  
    brands = crawler.crawl_brands()
    
    # 
    if brands:
        crawler.save_to_json(brands, "data/raw/gdpp_brands.json")
        
        #  
        print(f"\n :")
        print(f"  -   : {len(brands)}")
        
        #  
        categories = {}
        for brand in brands:
            cat = brand.get('category', '')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"  -  :")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {cat}: {count}")
    else:
        print("\n    . HTML  .")
