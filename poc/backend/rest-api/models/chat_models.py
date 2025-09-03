from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Model for chat request"""
    user_prompt: str = Field(..., description="User's legal question or prompt", min_length=1, max_length=2000)
    chat_id: Optional[str] = Field(None, description="Optional chat session ID for conversation continuity")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens for response", ge=100, le=4000)
    temperature: Optional[float] = Field(0.7, description="Temperature for response generation", ge=0.0, le=2.0)

# class Citation(BaseModel):
#     """Model for legal citation"""
#     law_name: str = Field(..., description="Name of the Israeli law")
#     section: Optional[str] = Field(None, description="Specific section reference")
#     chapter: Optional[str] = Field(None, description="Chapter reference")
#     part: Optional[str] = Field(None, description="Part reference")
#     sign: Optional[str] = Field(None, description="Sign reference")
#     text_excerpt: str = Field(..., description="Relevant text excerpt from the law")
#     relevance_score: Optional[float] = Field(None, description="Relevance score from vector search")

class ChatResponse(BaseModel):
    """Model for chat response"""
    answer: str = Field(..., description="Generated legal opinion/answer")
    # citations: List[Citation] = Field(default_factory=list, description="List of legal citations supporting the answer")
    chat_id: str = Field(..., description="Chat session ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_seconds: Optional[float] = Field(None, description="Time taken to generate response")

class StreamingChatResponse(BaseModel):
    """Model for streaming chat response chunk"""
    content: str = Field(..., description="Content chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    # citations: Optional[List[Citation]] = Field(None, description="Citations (only in final chunk)")
    chat_id: str = Field(..., description="Chat session ID")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    chat_id: Optional[str] = Field(None, description="Chat session ID if applicable")