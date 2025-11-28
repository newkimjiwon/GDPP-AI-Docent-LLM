# File: src/rag/embedder.py
"""
임베딩 모듈 - Ko-SBERT를 사용한 텍스트 임베딩
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from pathlib import Path


class KoSBERTEmbedder:
    """Ko-SBERT 모델을 사용한 한국어 텍스트 임베딩"""
    
    def __init__(self, model_name: str = "jhgan/ko-sbert-nli"):
        """
        Args:
            model_name: 사용할 임베딩 모델 이름
        """
        print(f"[INFO] 임베딩 모델 로드 중: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"[SUCCESS] 모델 로드 완료 (임베딩 차원: {self.embedding_dim})")
        
    def embed_documents(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        문서 리스트를 벡터로 변환
        
        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            임베딩 벡터 배열 (shape: [len(texts), embedding_dim])
        """
        print(f"[INFO] {len(texts)}개 문서 임베딩 중...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        print(f"[SUCCESS] 임베딩 완료 (shape: {embeddings.shape})")
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        검색 쿼리를 벡터로 변환
        
        Args:
            query: 검색 쿼리 텍스트
            
        Returns:
            임베딩 벡터 (shape: [embedding_dim])
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        return self.embedding_dim


if __name__ == "__main__":
    # 테스트
    embedder = KoSBERTEmbedder()
    
    # 샘플 텍스트
    texts = [
        "고양이는 귀여운 동물입니다.",
        "강아지는 충성스러운 반려동물입니다.",
        "고양이 사료를 추천해주세요."
    ]
    
    # 문서 임베딩
    doc_embeddings = embedder.embed_documents(texts)
    print(f"\n[STATS] 문서 임베딩 결과:")
    print(f"  - 문서 수: {len(texts)}")
    print(f"  - 임베딩 shape: {doc_embeddings.shape}")
    
    # 쿼리 임베딩
    query = "고양이에 대해 알려주세요"
    query_embedding = embedder.embed_query(query)
    print(f"\n[STATS] 쿼리 임베딩 결과:")
    print(f"  - 쿼리: {query}")
    print(f"  - 임베딩 shape: {query_embedding.shape}")
    
    # 유사도 계산 (코사인 유사도)
    from numpy.linalg import norm
    similarities = []
    for i, doc_emb in enumerate(doc_embeddings):
        similarity = np.dot(query_embedding, doc_emb) / (norm(query_embedding) * norm(doc_emb))
        similarities.append((i, similarity))
        print(f"  - 문서 {i+1} 유사도: {similarity:.4f}")
    
    # 가장 유사한 문서
    most_similar = max(similarities, key=lambda x: x[1])
    print(f"\n[RESULT] 가장 유사한 문서: {most_similar[0]+1} (유사도: {most_similar[1]:.4f})")
    print(f"  내용: {texts[most_similar[0]]}")
