from pydantic import BaseModel
from typing import List, Any

class ChatRequest(BaseModel):
    question: str
    chat_history: List[Any] = [] # LangChain's memory objects can be complex

class ChatResponse(BaseModel):
    answer: str
    chat_history: List[Any]