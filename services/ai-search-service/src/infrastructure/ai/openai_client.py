"""OpenAI integration for embeddings and completions"""
import openai
from typing import List
from src.config.settings import get_settings

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using OpenAI
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    response = await openai.Embedding.acreate(
        model=settings.EMBEDDING_MODEL,
        input=text
    )
    return response['data'][0]['embedding']


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    response = await openai.Embedding.acreate(
        model=settings.EMBEDDING_MODEL,
        input=texts
    )
    return [item['embedding'] for item in response['data']]


async def generate_query_completion(query: str) -> str:
    """
    Generate query completion/expansion using GPT
    
    Args:
        query: User query
        
    Returns:
        Completed/expanded query
    """
    response = await openai.ChatCompletion.acreate(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that expands user search queries into more descriptive versions for product search."},
            {"role": "user", "content": f"Expand this search query: {query}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content
