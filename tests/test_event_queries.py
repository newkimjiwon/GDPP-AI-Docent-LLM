"""
Test event-related queries with the updated vector DB
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
    "궁디팡팡 캣페스타 사무국 연락처 알려줘",
    "2025년 궁팡 일정이 어떻게 되나요?",
    "반려동물 동반 입장 가능한가요?",
    "무료입장 대상은 누구인가요?",
    "사전예매 취소는 어떻게 하나요?"
]

print("=" * 60)
print("이벤트 관련 질의 테스트")
print("=" * 60)

for query in test_queries:
    print(f"\n[QUERY] {query}")
    query_embedding = embedder.embed_query(query)
    results = vector_store.similarity_search(query_embedding, k=2)
    
    print(f"[RESULTS] 상위 2개 결과:")
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] (거리: {result['distance']:.4f})")
        print(f"      {result['document'][:150]}...")
        print(f"      소스: {result['metadata']['source']}")
