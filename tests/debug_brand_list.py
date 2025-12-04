"""
Debug script to find the correct regex pattern for brand_list
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://gdppcat.com/brand"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

scripts = soup.find_all('script')

for i, script in enumerate(scripts):
    if script.string and 'brand_list:' in script.string:
        print(f"Found brand_list in script {i}")
        
        # Find the start of brand_list
        start_idx = script.string.find('brand_list:')
        if start_idx != -1:
            # Get a snippet around it
            snippet = script.string[start_idx:start_idx+500]
            print(f"\nSnippet:\n{snippet}\n")
            
            # Try to find where the array ends
            # Look for the pattern: brand_list: [...],
            # We need to count brackets
            array_start = script.string.find('[', start_idx)
            if array_start != -1:
                bracket_count = 0
                in_string = False
                escape_next = False
                
                for j, char in enumerate(script.string[array_start:], start=array_start):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
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
                                print(f"Array ends at position {array_end}")
                                print(f"Array length: {array_end - array_start} characters")
                                
                                # Save to file for inspection
                                with open('brand_list_raw.json', 'w', encoding='utf-8') as f:
                                    f.write(script.string[array_start:array_end])
                                print("Saved to brand_list_raw.json")
                                break
        break
