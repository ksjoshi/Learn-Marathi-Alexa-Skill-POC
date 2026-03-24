from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Search Pydantic Models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results to return")

class SearchResult(BaseModel):
    content: str
    content_english: Optional[str]
    metadata: Optional[Dict[str, Any]]
    similarity: float

class SearchResponse(BaseModel):
    success: bool
    count: int
    results: List[SearchResult]

# Translation Pydantic Models
class TranslateRequest(BaseModel):
    phrase: str = Field(..., description="Text to translate from English to Marathi")

class TranslateResponse(BaseModel):
    success: bool
    translated_text: str
    error: Optional[str] = None

# RAG Pydantic Models
class AskRequest(BaseModel):
    query: str = Field(..., description="Question to answer")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context documents")

class AskResponse(BaseModel):
    success: bool
    answer: str
    context_used: int
    top_similarity: Optional[float]
    error: Optional[str] = None

# Health Pydantic Models
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
