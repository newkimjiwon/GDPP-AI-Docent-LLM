# File: src/model/ollama_client.py
"""
Ollama API 클라이언트
"""
import requests
import json
from typing import Generator, Dict, List, Optional


class OllamaClient:
    """Ollama API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "eeve-korean-10.8b:latest"):
        """
        Args:
            base_url: Ollama API 서버 URL
            model: 사용할 모델 이름
        """
        self.base_url = base_url
        self.model = model
        
    def check_connection(self) -> bool:
        """Ollama 서버 연결 확인"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """사용 가능한 모델 목록 조회"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            print(f"[ERROR] 모델 목록 조회 실패: {e}")
            return []
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        텍스트 생성 (비스트리밍)
        
        Args:
            prompt: 사용자 프롬프트
            system: 시스템 프롬프트
            temperature: 온도 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(url, json=payload, timeout=600)
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"[ERROR] API 호출 실패: {response.status_code}"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> Generator[str, None, None]:
        """
        텍스트 생성 (스트리밍)
        
        Args:
            prompt: 사용자 프롬프트
            system: 시스템 프롬프트
            temperature: 온도 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수
            
        Yields:
            생성된 텍스트 청크
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=600)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"[ERROR] API 호출 실패: {response.status_code}"
                
        except Exception as e:
            yield f"[ERROR] {str(e)}"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        채팅 형식으로 텍스트 생성
        
        Args:
            messages: 메시지 리스트 [{"role": "user", "content": "..."}]
            temperature: 온도
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=600)
            if response.status_code == 200:
                return response.json()['message']['content']
            else:
                return f"[ERROR] API 호출 실패: {response.status_code}"
        except Exception as e:
            return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # 테스트
    client = OllamaClient()
    
    # 연결 확인
    print("[INFO] Ollama 서버 연결 확인...")
    if client.check_connection():
        print("[SUCCESS] Ollama 서버 연결 성공")
        
        # 모델 목록
        models = client.list_models()
        print(f"\n[INFO] 사용 가능한 모델: {len(models)}개")
        for model in models:
            print(f"  - {model['name']}")
        
        # 간단한 테스트
        print("\n[TEST] 텍스트 생성 테스트")
        prompt = "고양이에 대해 한 문장으로 설명해주세요."
        response = client.generate(prompt, temperature=0.3, max_tokens=100)
        print(f"[RESPONSE] {response}")
        
        # 스트리밍 테스트
        print("\n[TEST] 스트리밍 생성 테스트")
        print("[RESPONSE] ", end="", flush=True)
        for chunk in client.generate_stream(prompt, temperature=0.3, max_tokens=100):
            print(chunk, end="", flush=True)
        print()
        
    else:
        print("[ERROR] Ollama 서버에 연결할 수 없습니다.")
        print("[INFO] Ollama가 설치되어 있고 실행 중인지 확인하세요:")
        print("  $ ollama serve")
