import logging
import google.generativeai as genai
from config import Config
from prompts import ChatPrompts

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, api_key: str = None):
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
        conversation_history: list[dict] = None,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> str:
        try:
            # Build prompt with context and chat history
            prompt = self._build_prompt(query, context_chunks, conversation_history)

            model = genai.GenerativeModel(self.chat_model)

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p
            )

            response = model.generate_content(prompt, generation_config=generation_config)

            answer = response.text
            logger.info(f'Generated response for query: {query[:50]}...')
            return answer

        except Exception as e:
            error_msg = str(e)
            # Handle rate limit errors
            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                logger.error(f'Gemini API rate limit exceeded: {e}')
                raise ValueError('API rate limit exceeded. Please try again in a moment.')
            logger.exception(f'Failed to generate response: {e}')
            raise
    
    def generate_general_response(self, query: str, conversation_history: list[dict] = None, temperature: float = 0.7, top_p: float = 0.95) -> str:
        try:
            prompt = ChatPrompts.build_general_prompt(query, conversation_history)

            model = genai.GenerativeModel(self.chat_model)

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p
            )

            response = model.generate_content(prompt, generation_config=generation_config)

            answer = response.text
            logger.info(f'Generated general response for query: {query[:50]}...')
            return answer

        except Exception as e:
            error_msg = str(e)
            # Handle rate limit errors
            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                logger.error(f'Gemini API rate limit exceeded: {e}')
                raise ValueError('API rate limit exceeded. Please try again in a moment.')
            logger.exception(f'Failed to generate general response: {e}')
            raise

    def _build_prompt(self, query: str, context_chunks: list[str], conversation_history: list[dict] = None) -> str:
        return ChatPrompts.build_rag_prompt(query, context_chunks, conversation_history)
