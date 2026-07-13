import logging
from fastapi import APIRouter, HTTPException

from services import (
    GeminiEmbeddingService,
    ChatService,
    RetrievalService,
    ChatMemoryService
)
from database import ChromaManager
from models import QueryRequest, QueryResponse, QueryData

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
    # Quick check for common greetings and short queries
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
                 'good evening', 'how are you', 'what can you do', 'who are you',
                 'what are you', 'help', 'thanks', 'thank you', 'bye', 'goodbye']
    query_lower = query.lower().strip()
    return any(greeting in query_lower for greeting in greetings) or len(query.split()) <= 3

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        session_id = request.session_id or "default_session"

        conversation_history = memory_service.get_history(session_id, last_n=10)

        # Handle greetings without document search
        if _is_greeting_or_general(query):
            answer = chat_service.generate_general_response(
                query,
                conversation_history,
                temperature=request.temperature,
                top_p=request.top_p
            )
            memory_service.add_message(session_id, "user", query)
            memory_service.add_message(session_id, "assistant", answer)
            logger.info(f'Handled general query: {query[:50]}...')

            response_metadata = {
                "used_documents": [],
                "conversation_history": conversation_history
            }

            return QueryResponse(
                success=True,
                data=QueryData(
                    answer=answer,
                    session_id=session_id,
                    metadata=response_metadata
                )
            )

        # Search for relevant document chunks with dynamic top_k
        retrieval_results = retrieval_service.retrieve_relevant_chunks(query, top_k=request.top_k)

        # Fall back to general response if no relevant docs found
        if not retrieval_results['chunks']:
            answer = chat_service.generate_general_response(
                query,
                conversation_history,
                temperature=request.temperature,
                top_p=request.top_p
            )
            memory_service.add_message(session_id, "user", query)
            memory_service.add_message(session_id, "assistant", answer)
            logger.info(f'No documents found, using general response for: {query[:50]}...')

            response_metadata = {
                "used_documents": [],
                "conversation_history": conversation_history
            }

            return QueryResponse(
                success=True,
                data=QueryData(
                    answer=answer,
                    session_id=session_id,
                    metadata=response_metadata
                )
            )

        answer = chat_service.generate_response(
            query=query,
            context_chunks=retrieval_results['chunks'],
            conversation_history=conversation_history,
            temperature=request.temperature,
            top_p=request.top_p
        )

        memory_service.add_message(session_id, "user", query)
        memory_service.add_message(session_id, "assistant", answer)

        logger.info(f'Query processed successfully: {query[:50]}...')

        # Extract unique document names for metadata
        used_documents = set()
        for source in retrieval_results['sources']:
            if 'filename' in source['metadata']:
                used_documents.add(source['metadata']['filename'])

        response_metadata = {
            "used_documents": sorted(list(used_documents)),
            "conversation_history": conversation_history
        }

        return QueryResponse(
            success=True,
            data=QueryData(
                answer=answer,
                session_id=session_id,
                metadata=response_metadata
            )
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle API errors (rate limits, etc.)
        error_msg = str(e)
        logger.error(f'Query failed with value error: {error_msg}')
        raise HTTPException(status_code=429 if 'rate limit' in error_msg.lower() else 400, detail=error_msg)
    except Exception as e:
        logger.exception(f'Query failed: {e}')
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )

@router.post("/session/new")
async def create_new_session():
    try:
        # User clicked "New Chat" - wipe old sessions
        session_id = memory_service.create_session(clear_old=True)
        logger.info(f'Created new session with old sessions cleared: {session_id}')
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

@router.post("/clear/{session_id}")
async def clear_session(session_id: str):
    try:
        memory_service.clear_session(session_id)
        logger.info(f'Cleared chat history')
        return {
            "success": True,
            "message": "Chat history cleared"
        }
    except Exception as e:
        logger.exception(f'Failed to clear session: {e}')
        raise HTTPException(
            status_code=500,
            detail="Failed to clear session"
        )
