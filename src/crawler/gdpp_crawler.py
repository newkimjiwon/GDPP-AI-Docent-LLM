# File: src/crawler/gdpp_crawler.py
"""
GDPP    - Selenium 
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
from pathlib import Path


class GDPPBrandCrawler:
    """   """
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless:    
        """
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Selenium WebDriver """
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def close_driver(self):
        """WebDriver """
        if self.driver:
            self.driver.quit()
            
    def crawl_brands(self, url: str = "https://gdppcat.com/brand") -> List[Dict]:
        """  """
        
        print(f"    : {url}")
        
        try:
            self.setup_driver()
            self.driver.get(url)
            
            # 페이지 로딩 대기
            print("[INFO] 페이지 로딩 대기 중...")
            time.sleep(3)
            
            #    
            print("   ...")
            self.scroll_page()
            
            #   
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            #    ( HTML    )
            brands = self.extract_brands(soup)
            
            print(f" {len(brands)}    ")
            
            return brands
            
        except Exception as e:
            print(f"    : {e}")
            return []
            
        finally:
            self.close_driver()
    
    def scroll_page(self):
        """    """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            #   
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            #   
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
    
    def extract_brands(self, soup: BeautifulSoup) -> List[Dict]:
        """HTML   """
        brands = []
        
        #  HTML     
        # :      div   
        
        #  1:   
        brand_elements = soup.find_all('div', class_=lambda x: x and 'brand' in x.lower())
        
        if not brand_elements:
            #  2:      
            brand_elements = soup.find_all('a', href=lambda x: x and '/brand/' in str(x))
        
        print(f" {len(brand_elements)}   ")
        
        for element in brand_elements:
            try:
                brand_info = self.parse_brand_element(element)
                if brand_info:
                    brands.append(brand_info)
            except Exception as e:
                print(f"    : {e}")
                continue
        
        return brands
    
    def parse_brand_element(self, element) -> Dict:
        """    """
        
        # 
        brand_name = element.get_text(strip=True)
        
        #  URL
        img_tag = element.find('img')
        image_url = img_tag.get('src', '') if img_tag else ''
        
        #  (    )
        category = element.get('data-category', '')
        
        #  ( )
        description = ''
        desc_element = element.find('p') or element.find('div', class_='description')
        if desc_element:
            description = desc_element.get_text(strip=True)
        
        return {
            "brand_name": brand_name,
            "category": category,
            "description": description,
            "image_url": image_url,
            "source_url": "https://gdppcat.com/brand"
        }
    
    def save_to_json(self, data: List[Dict], filepath: str):
        """ JSON  """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"   : {filepath}")


if __name__ == "__main__":
    #  
    crawler = GDPPBrandCrawler(headless=False)  #    
    
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
