"""
Test booth number queries
"""
import sys
sys.path.append('.')

from src.rag.embedder import KoSBERTEmbedder
from src.rag.vector_store import VectorStore

# Initialize
embedder = KoSBERTEmbedder()
vector_store = VectorStore(persist_directory="./data/vectordb", collection_name="gdpp_knowledge")

# Test queries
test_queries = [
    "페티코는 어떤거 판매하는 곳이야?",
    "1-G12 부스 번호는 뭐가 있어?",
    "건강백서캣 부스 번호 알려줘"
]

print("=" * 60)
print("부스 번호 질의 테스트")
print("=" * 60)

for query in test_queries:
    print(f"\n[QUERY] {query}")
    query_embedding = embedder.embed_query(query)
    results = vector_store.similarity_search(query_embedding, k=2)
    
    print(f"[RESULTS] 상위 2개 결과:")
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] (거리: {result['distance']:.4f})")
        print(f"      {result['document'][:200]}...")
        print(f"      소스: {result['metadata']['source']}")
        if 'booth_number' in result['metadata']:
            print(f"      부스: {result['metadata']['booth_number']}")
