class ChatPrompts:
    RAG_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's question based on the provided context.

If the context doesn't contain relevant information to answer the question, clearly state that you don't have enough information.

Be concise and accurate. Use only the information from the context below."""

    @staticmethod
    def build_rag_prompt(query: str, context_chunks: list[str]) -> str:
        """
        Build RAG prompt with context and query.
        
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
        
        prompt = f"""{ChatPrompts.RAG_SYSTEM_PROMPT}

{context}

Question: {query}

Answer:"""
        
        return prompt
    
    @staticmethod
    def build_summarization_prompt(text: str) -> str:
        """
        Build summarization prompt.
        
        Args:
            text: Text to summarize
            
        Returns:
            str: Formatted prompt
        """
        return f"""Summarize the following text concisely:

{text}

Summary:"""
    
    @staticmethod
    def build_extraction_prompt(text: str, entity_type: str) -> str:
        """
        Build entity extraction prompt.
        
        Args:
            text: Text to extract from
            entity_type: Type of entity to extract
            
        Returns:
            str: Formatted prompt
        """
        return f"""Extract all {entity_type} from the following text:

{text}

{entity_type}:"""
