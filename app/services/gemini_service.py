import google.generativeai as genai
from typing import List, Dict
from app.config import Config

class GeminiService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=self.api_key)
        self.embed_model = Config.GEMINI_EMBED_MODEL
        self.chat_model = Config.GEMINI_CHAT_MODEL
    
    def generate_embeddings(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self.embed_model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def generate_query_embedding(self, query: str) -> List[float]:
        result = genai.embed_content(
            model=self.embed_model,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def generate_response(self, query: str, context_chunks: List[str]) -> str:
        context = "\n\n".join([f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are a helpful assistant. Answer the user's question based on the provided context.
If the context doesn't contain relevant information, say so clearly.

{context}

Question: {query}

Answer:"""
        
        model = genai.GenerativeModel(self.chat_model)
        response = model.generate_content(prompt)
        return response.text
