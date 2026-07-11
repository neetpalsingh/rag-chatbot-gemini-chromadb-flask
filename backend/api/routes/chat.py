import logging
from fastapi import APIRouter, HTTPException

from services import (
    GeminiEmbeddingService,
    ChatService,
    RetrievalService
)
from database import ChromaManager
from models import QueryRequest, QueryResponse, QueryData, SourceInfo

logger = logging.getLogger(__name__)

router = APIRouter()

embedding_service = GeminiEmbeddingService()
chat_service = ChatService()
chroma_manager = ChromaManager()
retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    chroma_manager=chroma_manager
)

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query endpoint for chatbot.
    Retrieves relevant chunks and generates response asynchronously.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        retrieval_results = retrieval_service.retrieve_relevant_chunks(query)
        
        if not retrieval_results['chunks']:
            return QueryResponse(
                success=True,
                data=QueryData(
                    answer='No relevant documents found. Please upload documents first.',
                    sources=[]
                )
            )
        
        answer = chat_service.generate_response(
            query=query,
            context_chunks=retrieval_results['chunks']
        )
        
        logger.info(f'Query processed successfully: {query[:50]}...')
        
        sources = [
            SourceInfo(
                text=source['text'],
                metadata=source['metadata'],
                similarity_score=source['similarity_score']
            )
            for source in retrieval_results['sources']
        ]
        
        return QueryResponse(
            success=True,
            data=QueryData(
                answer=answer,
                sources=sources
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Query failed: {e}')
        raise HTTPException(
            status_code=500,
            detail="Failed to process query"
        )
