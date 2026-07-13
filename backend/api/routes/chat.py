import logging
from fastapi import APIRouter, HTTPException

from services import (
    GeminiEmbeddingService,
    ChatService,
    RetrievalService,
    ChatMemoryService
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
memory_service = ChatMemoryService()

def _is_greeting_or_general(query: str) -> bool:
    """Check if query is a greeting or general conversation."""
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
                 'good evening', 'how are you', 'what can you do', 'who are you',
                 'what are you', 'help', 'thanks', 'thank you', 'bye', 'goodbye']
    query_lower = query.lower().strip()
    return any(greeting in query_lower for greeting in greetings) or len(query.split()) <= 3

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query endpoint for chatbot with session memory.
    Retrieves relevant chunks and generates response asynchronously.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        session_id = request.session_id
        if not session_id or not memory_service.session_exists(session_id):
            session_id = memory_service.create_session()
            logger.info(f'Created new session: {session_id}')

        conversation_history = memory_service.get_history(session_id, last_n=10)

        if _is_greeting_or_general(query):
            answer = chat_service.generate_general_response(query, conversation_history)
            memory_service.add_message(session_id, "user", query)
            memory_service.add_message(session_id, "assistant", answer)
            logger.info(f'Handled general query: {query[:50]}...')
            return QueryResponse(
                success=True,
                data=QueryData(
                    answer=answer,
                    sources=[],
                    session_id=session_id
                )
            )

        retrieval_results = retrieval_service.retrieve_relevant_chunks(query)

        if not retrieval_results['chunks']:
            answer = chat_service.generate_general_response(query, conversation_history)
            memory_service.add_message(session_id, "user", query)
            memory_service.add_message(session_id, "assistant", answer)
            logger.info(f'No documents found, using general response for: {query[:50]}...')
            return QueryResponse(
                success=True,
                data=QueryData(
                    answer=answer,
                    sources=[],
                    session_id=session_id
                )
            )

        answer = chat_service.generate_response(
            query=query,
            context_chunks=retrieval_results['chunks'],
            conversation_history=conversation_history
        )

        memory_service.add_message(session_id, "user", query)
        memory_service.add_message(session_id, "assistant", answer)
        
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
                sources=sources,
                session_id=session_id
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

@router.post("/session/new")
async def create_new_session():
    """
    Create a new chat session.
    Used when user refreshes or wants to start fresh.
    """
    try:
        session_id = memory_service.create_session()
        logger.info(f'Created new session: {session_id}')
        return {
            "success": True,
            "session_id": session_id,
            "message": "New session created"
        }
    except Exception as e:
        logger.exception(f'Failed to create session: {e}')
        raise HTTPException(
            status_code=500,
            detail="Failed to create session"
        )

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session.
    Removes all conversation history for the session.
    """
    try:
        memory_service.clear_session(session_id)
        logger.info(f'Cleared session: {session_id}')
        return {
            "success": True,
            "message": "Session cleared"
        }
    except Exception as e:
        logger.exception(f'Failed to clear session: {e}')
        raise HTTPException(
            status_code=500,
            detail="Failed to clear session"
        )
