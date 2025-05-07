"""
Prompt templates for LLM generation.
"""

RAG_PROMPT_TEMPLATE = """
You are a helpful AI assistant that answers questions based on the provided context. 
Your goal is to give accurate, helpful, and concise answers based ONLY on the context provided.

CONTEXT:
{context}

USER QUERY:
{query}

INSTRUCTIONS:
1. Answer the user's query based ONLY on the information in the provided context.
2. If the context doesn't contain enough information to answer the query fully, say so clearly.
3. Do not make up information or use your general knowledge beyond what's in the context.
4. Keep your answer concise and to the point.
5. If the question is not related to the context, politely inform the user that you can only answer based on the provided context.

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
