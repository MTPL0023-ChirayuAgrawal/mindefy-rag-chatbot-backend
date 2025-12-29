"""
Embedding generation service using OpenAI
"""
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

class EmbeddingService:
    """Handles embedding generation using OpenAI."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        # Delay OpenAI client construction until first use so importing
        # modules does not fail when OPENAI_API_KEY is not set.
        self._client = None
        self.model = model

    def _ensure_client(self):
        if self._client is None:
            try:
                self._client = OpenAI()
            except Exception as e:
                # Provide a clear runtime error explaining what's missing
                raise RuntimeError(
                    "OpenAI client could not be initialized. "
                    "Set the OPENAI_API_KEY environment variable or pass an API key to the client." 
                    f"Original error: {e}"
                )
    
    def _process_batch(self, batch: List[str]) -> List[List[float]]:
        """Process a single batch of embeddings."""
        response = self._client.embeddings.create(
            model=self.model,
            input=batch
        )
        return [d.embedding for d in response.data]
    
    async def get_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings asynchronously with concurrent batch processing."""
        self._ensure_client()
        
        # Process in batches with concurrency for faster processing
        batch_size = 100
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        
        # Use ThreadPoolExecutor for concurrent API calls
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                loop.run_in_executor(executor, self._process_batch, batch)
                for batch in batches
            ]
            results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_embeddings = []
        for batch_embeddings in results:
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts in batches to avoid token limits."""
        self._ensure_client()
        
        # Process in batches to avoid exceeding OpenAI's token limit
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self._client.embeddings.create(
                model=self.model,
                input=batch
            )
            all_embeddings.extend([d.embedding for d in response.data])
        
        return all_embeddings
