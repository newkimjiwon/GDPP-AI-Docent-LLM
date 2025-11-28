# File: src/rag/vector_store.py
"""
벡터 데이터베이스 모듈 - ChromaDB 사용
"""
import chromadb
from chromadb.config import Settings
import json
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np


class VectorStore:
    """ChromaDB를 사용한 벡터 데이터베이스 관리"""
    
    def __init__(self, persist_directory: str = "./data/vectordb", collection_name: str = "gdpp_knowledge"):
        """
        Args:
            persist_directory: 벡터 DB 저장 디렉토리
            collection_name: 컬렉션 이름
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # ChromaDB 클라이언트 초기화
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"[INFO] 기존 컬렉션 로드: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "GDPP AI Docent Knowledge Base"}
            )
            print(f"[INFO] 새 컬렉션 생성: {collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """
        문서와 임베딩을 벡터 DB에 추가
        
        Args:
            documents: 문서 텍스트 리스트
            embeddings: 임베딩 벡터 배열
            metadatas: 메타데이터 리스트
            ids: 문서 ID 리스트 (없으면 자동 생성)
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        print(f"[INFO] {len(documents)}개 문서를 벡터 DB에 추가 중...")
        
        # ChromaDB는 리스트 형태의 임베딩을 요구
        embeddings_list = embeddings.tolist()
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[SUCCESS] {len(documents)}개 문서 추가 완료")
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        유사도 기반 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            k: 반환할 문서 수
            filter_dict: 메타데이터 필터 (예: {"source": "gdpp_brand"})
            
        Returns:
            검색 결과 리스트 (문서, 메타데이터, 거리)
        """
        # 쿼리 임베딩을 리스트로 변환
        query_embedding_list = query_embedding.tolist()
        
        # 검색 수행
        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=k,
            where=filter_dict
        )
        
        # 결과 포맷팅
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """컬렉션 통계 반환"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }
    
    def delete_collection(self):
        """컬렉션 삭제"""
        self.client.delete_collection(name=self.collection_name)
        print(f"[INFO] 컬렉션 삭제됨: {self.collection_name}")


if __name__ == "__main__":
    # 테스트
    from embedder import KoSBERTEmbedder
    
    # 임베더 초기화
    embedder = KoSBERTEmbedder()
    
    # 벡터 스토어 초기화
    vector_store = VectorStore(
        persist_directory="./data/vectordb_test",
        collection_name="test_collection"
    )
    
    # 샘플 문서
    documents = [
        "고양이는 귀여운 동물입니다.",
        "강아지는 충성스러운 반려동물입니다.",
        "고양이 사료를 추천해주세요.",
        "건강백서캣은 고양이 건강 관리 전문 브랜드입니다."
    ]
    
    metadatas = [
        {"source": "wikipedia", "category": "동물"},
        {"source": "wikipedia", "category": "동물"},
        {"source": "user_query", "category": "질문"},
        {"source": "gdpp_brand", "category": "헬스케어"}
    ]
    
    # 임베딩 생성
    embeddings = embedder.embed_documents(documents)
    
    # 벡터 DB에 추가
    vector_store.add_documents(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # 통계 출력
    stats = vector_store.get_collection_stats()
    print(f"\n[STATS] 벡터 DB 통계:")
    print(f"  - 컬렉션: {stats['collection_name']}")
    print(f"  - 문서 수: {stats['document_count']}")
    
    # 검색 테스트
    query = "고양이 건강에 좋은 제품"
    query_embedding = embedder.embed_query(query)
    
    print(f"\n[INFO] 검색 쿼리: {query}")
    results = vector_store.similarity_search(query_embedding, k=3)
    
    print(f"\n[RESULT] 검색 결과 (상위 3개):")
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] (거리: {result['distance']:.4f})")
        print(f"      문서: {result['document']}")
        print(f"      소스: {result['metadata']['source']}")
        print(f"      카테고리: {result['metadata']['category']}")
