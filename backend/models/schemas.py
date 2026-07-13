from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query text")
    session_id: Optional[str] = Field(None, description="Chat session ID")

class SourceInfo(BaseModel):
    text: str
    metadata: Dict[str, Any]
    similarity_score: float

class QueryData(BaseModel):
    answer: str
    sources: List[SourceInfo]
    session_id: str

class QueryResponse(BaseModel):
    success: bool
    data: QueryData

class UploadData(BaseModel):
    id: str
    filename: str
    chunks_count: int
    category: str

class UploadResponse(BaseModel):
    success: bool
    message: str
    data: UploadData

class Document(BaseModel):
    id: str
    filename: str
    category: str
    file_type: str
    file_size: int
    chunks_count: int
    status: str
    collection_name: str
    uploaded_at: str

class DocumentsResponse(BaseModel):
    success: bool
    data: List[Document]

class DeleteResponse(BaseModel):
    success: bool
    message: str

class HealthResponse(BaseModel):
    success: bool
    message: str

class StatsData(BaseModel):
    total_chunks: int

class StatsResponse(BaseModel):
    success: bool
    data: StatsData
