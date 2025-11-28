# File: src/model/__init__.py
"""
모델 모듈 초기화
"""
from .ollama_client import OllamaClient
from .prompt_template import PromptTemplate, create_chat_prompt

__all__ = ['OllamaClient', 'PromptTemplate', 'create_chat_prompt']
