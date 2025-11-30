# File: src/rag/build_vectordb.py
"""
벡터 데이터베이스 구축 스크립트
전처리된 청크 데이터를 임베딩하여 ChromaDB에 저장
"""
import json
from pathlib import Path
from embedder import KoSBERTEmbedder
from vector_store import VectorStore


def build_vector_database(
    chunks_file: str = "./data/processed/all_chunks.json",
    persist_directory: str = "./data/vectordb",
    collection_name: str = "gdpp_knowledge"
):
    """
    청크 데이터로부터 벡터 데이터베이스 구축
    
    Args:
        chunks_file: 전처리된 청크 JSON 파일 경로
        persist_directory: 벡터 DB 저장 디렉토리
        collection_name: 컬렉션 이름
    """
    print("=" * 60)
    print("[START] 벡터 데이터베이스 구축 시작")
    print("=" * 60)
    
    # 1. 청크 데이터 로드
    print(f"\n[STEP 1] 청크 데이터 로드: {chunks_file}")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"[INFO] 총 {len(chunks)}개 청크 로드됨")
    
    # 2. 임베더 초기화
    print(f"\n[STEP 2] 임베딩 모델 초기화")
    embedder = KoSBERTEmbedder(model_name="jhgan/ko-sbert-nli")
    
    # 3. 문서 텍스트 및 메타데이터 추출
    print(f"\n[STEP 3] 문서 및 메타데이터 추출")
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk['text'])
        metadatas.append(chunk['metadata'])
        ids.append(f"chunk_{i}")
    
    print(f"[INFO] {len(documents)}개 문서 준비 완료")
    
    # 4. 임베딩 생성
    print(f"\n[STEP 4] 임베딩 생성")
    embeddings = embedder.embed_documents(documents, batch_size=32)
    
    # 5. 벡터 스토어 초기화
    print(f"\n[STEP 5] 벡터 스토어 초기화")
    vector_store = VectorStore(
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    # 6. 벡터 DB에 문서 추가
    print(f"\n[STEP 6] 벡터 DB에 문서 추가")
    vector_store.add_documents(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    # 7. 통계 출력
    print(f"\n[STEP 7] 벡터 DB 통계")
    stats = vector_store.get_collection_stats()
    print(f"  - 컬렉션: {stats['collection_name']}")
    print(f"  - 문서 수: {stats['document_count']}")
    print(f"  - 저장 위치: {stats['persist_directory']}")
    
    # 8. 소스별 통계
    source_counts = {}
    for metadata in metadatas:
        source = metadata['source']
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\n[STATS] 소스별 문서 분포:")
    for source, count in source_counts.items():
        print(f"  - {source}: {count}개")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 벡터 데이터베이스 구축 완료!")
    print("=" * 60)
    
    return vector_store


if __name__ == "__main__":
    # 벡터 데이터베이스 구축
    vector_store = build_vector_database()
    
    # 간단한 검색 테스트
    print("\n\n" + "=" * 60)
    print("[TEST] 검색 기능 테스트")
    print("=" * 60)
    
    from embedder import KoSBERTEmbedder
    embedder = KoSBERTEmbedder()
    
    test_queries = [
        "고양이 사료 추천해줘",
        "건강백서캣에 대해 알려줘",
        "고양이 품종은 어떤 것들이 있나요?"
    ]
    
    for query in test_queries:
        print(f"\n[QUERY] {query}")
        query_embedding = embedder.embed_query(query)
        results = vector_store.similarity_search(query_embedding, k=3)
        
        print(f"[RESULTS] 상위 3개 결과:")
        for i, result in enumerate(results, 1):
            print(f"\n  [{i}] (거리: {result['distance']:.4f})")
            print(f"      {result['document'][:100]}...")
            print(f"      소스: {result['metadata']['source']}")
