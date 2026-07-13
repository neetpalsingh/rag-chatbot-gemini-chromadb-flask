import logging
import google.generativeai as genai
from config import Config
from prompts import ChatPrompts

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for generating chat responses using Google Gemini API.
    Constructs prompts with retrieved context and generates responses.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini chat model.
        
        Args:
            api_key: Gemini API key (defaults to config value)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=self.api_key)
        self.chat_model = Config.GEMINI_CHAT_MODEL
        logger.info(f'Chat service initialized with model: {self.chat_model}')
    
    def generate_response(
        self,
        query: str,
        context_chunks: list[str],
        conversation_history: list[dict] = None
    ) -> str:
        """
        Generate a response to the user query using retrieved context.

        Args:
            query: User question
            context_chunks: List of relevant text chunks from vector search
            conversation_history: Previous conversation messages

        Returns:
            str: Generated response
        """
        try:
            prompt = self._build_prompt(query, context_chunks, conversation_history)

            model = genai.GenerativeModel(self.chat_model)
            response = model.generate_content(prompt)

            answer = response.text
            logger.info(f'Generated response for query: {query[:50]}...')
            return answer

        except Exception as e:
            logger.exception(f'Failed to generate response: {e}')
            raise
    
    def generate_general_response(self, query: str, conversation_history: list[dict] = None) -> str:
        """
        Generate a response to general queries without context.

        Args:
            query: User question
            conversation_history: Previous conversation messages

        Returns:
            str: Generated response
        """
        try:
            prompt = ChatPrompts.build_general_prompt(query, conversation_history)

            model = genai.GenerativeModel(self.chat_model)
            response = model.generate_content(prompt)

            answer = response.text
            logger.info(f'Generated general response for query: {query[:50]}...')
            return answer

        except Exception as e:
            logger.exception(f'Failed to generate general response: {e}')
            raise

    def _build_prompt(self, query: str, context_chunks: list[str], conversation_history: list[dict] = None) -> str:
        """
        Build the prompt with context and query.

        Args:
            query: User question
            context_chunks: Retrieved context chunks
            conversation_history: Previous conversation messages

        Returns:
            str: Formatted prompt
        """
        return ChatPrompts.build_rag_prompt(query, context_chunks, conversation_history)
