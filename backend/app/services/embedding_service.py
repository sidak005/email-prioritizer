from sentence_transformers import SentenceTransformer
from typing import List
import torch


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    async def initialize(self):
        """Load the embedding model"""
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        print(f"✅ Embedding model loaded on {self.device}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch processing)"""
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return 384  # all-MiniLM-L6-v2 dimension
