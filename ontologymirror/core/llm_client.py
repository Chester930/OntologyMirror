import os
from enum import Enum
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import FakeListChatModel

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

class LLMClient:
    """
    Unified client for interacting with different LLM providers.
    Reads configuration from environment variables.
    """
    
    def __init__(self):
        # Allow override via env vars, default to MOCK for safety
        self.provider = os.getenv("LLM_PROVIDER", LLMProvider.MOCK)
        self.model = None
        self._setup_client()
        
    def _setup_client(self):
        if self.provider == LLMProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set")
            self.model = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                api_key=api_key,
                temperature=0
            )
            
        elif self.provider == LLMProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is not set")
            self.model = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
                google_api_key=api_key,
                temperature=0
            )
            
        else: # MOCK
            print("🤖 Using MOCK LLM (Logic-Based)")
            from .mock_llm import LogicBasedMockLLM
            self.model = LogicBasedMockLLM()

    def bind_json_output(self):
        """
        Returns a model that guarantees JSON output (if supported).
        """
        if self.provider == LLMProvider.OPENAI:
            return self.model.bind(response_format={"type": "json_object"})
        # Gemini handling for JSON mode varies, usually handled in prompt
        return self.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Simple generation method.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.model.invoke(messages)
        return response.content
