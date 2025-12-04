"""
Test script to inspect the actual HTML structure of GDPP brand page
"""
import requests
from bs4 import BeautifulSoup

url = "https://gdppcat.com/brand"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching: {url}\n")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Save the full HTML for inspection
with open('page_source.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("HTML saved to page_source.html")
print(f"Page title: {soup.title.string if soup.title else 'No title'}")
print(f"\nTotal divs: {len(soup.find_all('div'))}")
print(f"Total links: {len(soup.find_all('a'))}")

# Look for script tags that might contain brand data
scripts = soup.find_all('script')
print(f"\nTotal script tags: {len(scripts)}")

for i, script in enumerate(scripts):
    if script.string and ('brand' in script.string.lower() or 'PR_NAME' in script.string):
        print(f"\n--- Script {i} (contains brand data) ---")
        print(script.string[:500])  # First 500 chars
