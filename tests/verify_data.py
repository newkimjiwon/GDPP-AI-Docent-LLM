import json

# 데이터 로드
with open('data/raw/gdpp_brands.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'총 브랜드 수: {len(data)}')
print(f'\n샘플 브랜드 3개:')

for i in range(min(3, len(data))):
    b = data[i]
    print(f'\n{i+1}. {b["brand_name"]}')
    print(f'   부스: {b["booth_number"]}')
    print(f'   카테고리: {b["category"]}')
    print(f'   홈페이지: {b["homepage"][:50] if b["homepage"] else "없음"}')
    print(f'   인스타: {b["instagram"] if b["instagram"] else "없음"}')
