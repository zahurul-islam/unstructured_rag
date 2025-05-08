"""
Prompt templates for LLM generation.
"""

RAG_PROMPT_TEMPLATE = """
You are a helpful, friendly AI assistant that answers questions based on the provided document context.
Your goal is to give accurate, helpful, and natural-sounding answers based on the context provided.

CONTEXT:
{context}

USER QUERY:
{query}

INSTRUCTIONS:
1. Answer the user's query based ONLY on the information in the provided context.
2. Write in a conversational, friendly tone as if you're having a casual conversation.
3. Be thorough and detailed in your explanations, providing specific information from the documents.
4. ALWAYS begin your answer by directly addressing the user's question in a clear, concise way.
5. ALWAYS cite your sources by mentioning the specific documents you're referencing.
6. If the context contains information about the query, make sure to use it extensively in your answer.
7. If the context doesn't contain enough information to answer the query fully, clearly state what information is missing.
8. Format your response with paragraphs for readability.
9. Use bullet points when listing multiple items or steps.
10. NEVER make up information that isn't in the context.
11. NEVER say you don't have enough information if the context clearly contains relevant information.
12. If the query is about LLMs (Large Language Models), make sure to provide a comprehensive answer based on the context.
13. Pay special attention to acronyms like "LLM" and expand them in your answer (e.g., "LLM stands for Large Language Model").
14. When answering questions about technical topics, provide both a simple explanation and more detailed information.

YOUR ANSWER:
"""

SYSTEM_PROMPT = """
You are a helpful AI assistant that provides accurate information based on the documents and context provided to you.
Your goal is to be helpful, accurate, and concise.
"""

RERANK_PROMPT_TEMPLATE = """
QUERY:
{query}

PASSAGES:
{passages}

TASK:
Rate each passage on a scale of 1-10 based on its relevance to the query.
Provide your rating and a brief explanation for each passage.
Return the passages in order from most relevant to least relevant.
"""

SUMMARIZATION_PROMPT_TEMPLATE = """
The following are excerpts from one or more documents:

{context}

Provide a comprehensive summary that captures the key information from these excerpts.
Focus on factual information and main points that would be most helpful.
"""
