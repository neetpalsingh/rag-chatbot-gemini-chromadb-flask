class ChatPrompts:
    RAG_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's question based on the provided context.

If the context doesn't contain relevant information to answer the question, clearly state that you don't have enough information.

Be concise and accurate. Use only the information from the context below."""

    GENERAL_GREETING_PROMPT = """You are a friendly and helpful AI assistant specialized in answering questions from uploaded documents.

Respond naturally to greetings and general questions. If the user greets you or asks general questions, respond warmly and let them know you can help them with questions about their uploaded documents.

Be conversational, friendly, and helpful."""

    @staticmethod
    def build_rag_prompt(query: str, context_chunks: list[str], conversation_history: list[dict] = None) -> str:
        """
        Build RAG prompt with context and query.

        Args:
            query: User question
            context_chunks: Retrieved context chunks
            conversation_history: Previous conversation messages

        Returns:
            str: Formatted prompt
        """
        context = "\n\n".join([
            f"Context {idx + 1}:\n{chunk}"
            for idx, chunk in enumerate(context_chunks)
        ])

        history_text = ""
        if conversation_history:
            history_text = "\n\nConversation History:\n"
            for msg in conversation_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"

        prompt = f"""{ChatPrompts.RAG_SYSTEM_PROMPT}

{context}{history_text}

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

    @staticmethod
    def build_general_prompt(query: str, conversation_history: list[dict] = None) -> str:
        """
        Build prompt for general queries without context.

        Args:
            query: User question
            conversation_history: Previous conversation messages

        Returns:
            str: Formatted prompt
        """
        history_text = ""
        if conversation_history:
            history_text = "\n\nConversation History:\n"
            for msg in conversation_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"

        return f"""{ChatPrompts.GENERAL_GREETING_PROMPT}{history_text}

User: {query}
"""