# File: src/rag/hybrid_retriever.py
"""
하이브리드 검색 모듈 - Dense Vector + Sparse BM25
"""
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict, Tuple
import json
from .embedder import KoSBERTEmbedder
from .vector_store import VectorStore


class HybridRetriever:
    """Dense Vector Search와 Sparse BM25 Search를 결합한 하이브리드 검색기"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedder: KoSBERTEmbedder,
        chunks_file: str = "/mnt/d/Project/GDDPAIDocent/data/processed/all_chunks.json"
    ):
        """
        Args:
            vector_store: ChromaDB 벡터 스토어
            embedder: 임베딩 모델
            chunks_file: 청크 데이터 파일 (BM25 인덱스 구축용)
        """
        self.vector_store = vector_store
        self.embedder = embedder
        
        # 청크 데이터 로드
        print(f"[INFO] 청크 데이터 로드 중: {chunks_file}")
        with open(chunks_file, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        # BM25 인덱스 구축
        print(f"[INFO] BM25 인덱스 구축 중...")
        self.documents = [chunk['text'] for chunk in self.chunks]
        
        # 토큰화 (간단한 공백 기반)
        tokenized_docs = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f"[SUCCESS] BM25 인덱스 구축 완료 ({len(self.documents)}개 문서)")
    
    def vector_search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Dense Vector Search (의미 기반 검색)
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            
        Returns:
            검색 결과 리스트
        """
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.similarity_search(query_embedding, k=k)
        
        # 점수 정규화 (거리를 유사도로 변환)
        for result in results:
            # 거리가 작을수록 유사도가 높음
            # 거리를 0-1 범위의 유사도로 변환
            result['score'] = 1.0 / (1.0 + result['distance'])
            result['search_type'] = 'vector'
        
        return results
    
    def bm25_search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Sparse BM25 Search (키워드 기반 검색)
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            
        Returns:
            검색 결과 리스트
        """
        # 쿼리 토큰화
        tokenized_query = query.split()
        
        # BM25 점수 계산
        scores = self.bm25.get_scores(tokenized_query)
        
        # 상위 k개 문서 인덱스
        top_k_indices = np.argsort(scores)[::-1][:k]
        
        # 결과 포맷팅
        results = []
        for idx in top_k_indices:
            if scores[idx] > 0:  # 점수가 0보다 큰 경우만
                results.append({
                    "id": f"chunk_{idx}",
                    "document": self.documents[idx],
                    "metadata": self.chunks[idx]['metadata'],
                    "score": float(scores[idx]),
                    "search_type": "bm25"
                })
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> List[Dict]:
        """
        하이브리드 검색 (Vector + BM25)
        
        Args:
            query: 검색 쿼리
            k: 최종 반환할 문서 수
            vector_weight: Vector Search 가중치
            bm25_weight: BM25 Search 가중치
            
        Returns:
            검색 결과 리스트 (점수 기준 정렬)
        """
        # 각 검색 방법으로 더 많은 문서 검색 (k*2)
        vector_results = self.vector_search(query, k=k*2)
        bm25_results = self.bm25_search(query, k=k*2)
        
        # 문서 ID별로 점수 집계
        doc_scores = {}
        doc_data = {}
        
        # Vector Search 결과 처리
        for result in vector_results:
            doc_id = result['id']
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + result['score'] * vector_weight
            doc_data[doc_id] = result
        
        # BM25 Search 결과 처리
        for result in bm25_results:
            doc_id = result['id']
            
            # BM25 점수 정규화 (0-1 범위로)
            normalized_score = result['score'] / (result['score'] + 1.0)
            
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + normalized_score * bm25_weight
            
            if doc_id not in doc_data:
                doc_data[doc_id] = result
        
        # 점수 기준 정렬
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 k개 결과 반환
        final_results = []
        for doc_id, score in sorted_docs[:k]:
            result = doc_data[doc_id].copy()
            result['hybrid_score'] = score
            result['search_type'] = 'hybrid'
            final_results.append(result)
        
        return final_results


if __name__ == "__main__":
    # 테스트
    print("=" * 60)
    print("[TEST] 하이브리드 검색 테스트")
    print("=" * 60)
    
    # 초기화
    embedder = KoSBERTEmbedder()
    vector_store = VectorStore(
        persist_directory="/mnt/d/Project/GDDPAIDocent/data/vectordb",
        collection_name="gdpp_knowledge"
    )
    
    retriever = HybridRetriever(
        vector_store=vector_store,
        embedder=embedder
    )
    
    # 테스트 쿼리
    test_queries = [
        "고양이 사료 추천해줘",
        "건강백서캣",
        "고양이 품종"
    ]
    
    for query in test_queries:
        print(f"\n\n{'='*60}")
        print(f"[QUERY] {query}")
        print(f"{'='*60}")
        
        # Vector Search
        print(f"\n[Vector Search] 상위 3개:")
        vector_results = retriever.vector_search(query, k=3)
        for i, result in enumerate(vector_results, 1):
            print(f"  [{i}] (점수: {result['score']:.4f})")
            print(f"      {result['document'][:80]}...")
        
        # BM25 Search
        print(f"\n[BM25 Search] 상위 3개:")
        bm25_results = retriever.bm25_search(query, k=3)
        for i, result in enumerate(bm25_results, 1):
            print(f"  [{i}] (점수: {result['score']:.4f})")
            print(f"      {result['document'][:80]}...")
        
        # Hybrid Search
        print(f"\n[Hybrid Search] 상위 3개:")
        hybrid_results = retriever.hybrid_search(query, k=3)
        for i, result in enumerate(hybrid_results, 1):
            print(f"  [{i}] (점수: {result['hybrid_score']:.4f})")
            print(f"      {result['document'][:80]}...")
