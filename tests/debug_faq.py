"""
Debug FAQ HTML structure
"""
import requests
from bs4 import BeautifulSoup

url = "https://catfesta.com/information/visitor-faq/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all h4 tags
h4_tags = soup.find_all('h4')
print(f"Found {len(h4_tags)} h4 tags")

# Check first few
for i, h4 in enumerate(h4_tags[:5]):
    print(f"\n--- H4 {i+1} ---")
    print(f"Text: {h4.get_text(strip=True)[:100]}")
    print(f"HTML: {str(h4)[:200]}")
    
    # Check siblings
    next_elem = h4.find_next_sibling()
    if next_elem:
        print(f"Next sibling: {next_elem.name} - {next_elem.get_text(strip=True)[:100]}")

# Try finding FAQ content differently
print("\n\n=== Looking for FAQ patterns ===")
# Look for elements with FAQ-like content
for tag in soup.find_all(['div', 'section', 'article']):
    text = tag.get_text(strip=True)
    if 'Q.' in text and len(text) > 50:
        print(f"\nFound potential FAQ in {tag.name}:")
        print(f"Class: {tag.get('class')}")
        print(f"Text preview: {text[:150]}")
        break
