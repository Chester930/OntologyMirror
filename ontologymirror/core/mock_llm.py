from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class LogicBasedMockLLM(BaseChatModel):
    """
    A Mock LLM that returns different responses based on input content.
    """
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        last_message = messages[-1].content.lower()
        
        response_content = "{}"
        
        # Simple keyword matching to simulate "intelligence"
        # Prioritize Blog detection first
        if "blog" in last_message or "post" in last_message:
             response_content = """
            {
                "schema_class": "BlogPosting",
                "rationale": "Detected blog-related keywords.",
                "mappings": [
                    {"original_name": "title", "schema_property": "headline", "reason": "Mock logic"},
                    {"original_name": "content", "schema_property": "articleBody", "reason": "Mock logic"}
                ]
            }
            """
        elif "user" in last_message or "auth" in last_message:
            response_content = """
            {
                "schema_class": "Person",
                "rationale": "Detected user-related fields.",
                "mappings": [
                    {"original_name": "username", "schema_property": "alternateName", "reason": "Mock logic"},
                    {"original_name": "email", "schema_property": "email", "reason": "Mock logic"}
                ]
            }
            """
        else:
            response_content = """
            {
                "schema_class": "Thing",
                "rationale": "No specific context detected by Mock.",
                "mappings": []
            }
            """
            
        message = AIMessage(content=response_content)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        return "logic_mock"
