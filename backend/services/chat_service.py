import logging
import google.generativeai as genai
from config import Config

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
        context_chunks: list[str]
    ) -> str:
        """
        Generate a response to the user query using retrieved context.
        
        Args:
            query: User question
            context_chunks: List of relevant text chunks from vector search
            
        Returns:
            str: Generated response
        """
        try:
            prompt = self._build_prompt(query, context_chunks)
            
            model = genai.GenerativeModel(self.chat_model)
            response = model.generate_content(prompt)
            
            answer = response.text
            logger.info(f'Generated response for query: {query[:50]}...')
            return answer
            
        except Exception as e:
            logger.exception(f'Failed to generate response: {e}')
            raise
    
    def _build_prompt(self, query: str, context_chunks: list[str]) -> str:
        """
        Build the prompt with context and query.
        
        Args:
            query: User question
            context_chunks: Retrieved context chunks
            
        Returns:
            str: Formatted prompt
        """
        context = "\n\n".join([
            f"Context {idx + 1}:\n{chunk}"
            for idx, chunk in enumerate(context_chunks)
        ])
        
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context.

If the context doesn't contain relevant information to answer the question, clearly state that you don't have enough information.

Be concise and accurate. Use only the information from the context below.

{context}

Question: {query}

Answer:"""
        
        return prompt
