from typing import List

from backend.app.config import settings

# Lazy imports for local model (dev only); production uses HF API

HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.use_api = settings.environment == "production"
        self.model_name = HF_EMBEDDING_MODEL

    async def initialize(self):
        if self.use_api:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer(self.model_name, device=device)
        except ImportError:
            self.use_api = True

    def generate_embedding(self, text: str) -> List[float]:
        if self.use_api:
            return self._embed_via_api(text)
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        emb = self.model.encode(text, convert_to_numpy=True)
        return emb.tolist()

    def _embed_via_api(self, text: str) -> List[float]:
        import httpx
        if not getattr(settings, "huggingface_api_key", None):
            return [0.0] * EMBEDDING_DIM
        url = f"https://api-inference.huggingface.co/models/{HF_EMBEDDING_MODEL}"
        headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(url, headers=headers, json={"inputs": text[:8192]})
                r.raise_for_status()
                out = r.json()
                if isinstance(out, list) and out:
                    vec = out[0]
                    if isinstance(vec, list):
                        return vec
        except Exception:
            pass
        return [0.0] * EMBEDDING_DIM

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if self.use_api:
            return [self._embed_via_api(t) for t in texts]
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [e.tolist() for e in embs]

    def get_dimension(self) -> int:
        return EMBEDDING_DIM
