from typing import List, Dict, Optional

from backend.app.config import settings

# Handle different Pinecone versions
try:
    # Try new API (v3+)
    from pinecone import Pinecone, ServerlessSpec
    USE_NEW_API = True
except ImportError:
    USE_NEW_API = False
    Pinecone = None
    ServerlessSpec = None


class PineconeService:
    def __init__(self):
        self.pc = None
        self.index_name = settings.pinecone_index_name
        self.index = None
        self.dimension = 384  # For sentence-transformers/all-MiniLM-L6-v2
    
    async def initialize(self):
        """Initialize or connect to Pinecone index"""
        if not USE_NEW_API:
            raise ImportError("Pinecone v3+ required. Install: pip install 'pinecone>=3.0.0'")
        
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                # Create index if it doesn't exist
                print(f"Creating Pinecone index: {self.index_name}")
                region = settings.pinecone_environment
                if region and "-" in region:
                    parts = region.split("-")
                    if len(parts) >= 3:
                        region = f"{parts[0]}-{parts[1]}-{parts[2]}"
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=region or "us-east-1")
                )
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise
    
    async def upsert_email_embedding(
        self,
        email_id: str,
        embedding: List[float],
        metadata: Dict
    ):
        """Store email embedding in Pinecone"""
        if self.index is None:
            return
        
        try:
            self.index.upsert(vectors=[{
                "id": email_id,
                "values": embedding,
                "metadata": metadata
            }])
        except Exception as e:
            print(f"Error upserting embedding: {e}")
    
    async def search_similar_emails(
        self,
        embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar emails"""
        if self.index is None:
            return []
        
        try:
            query_response = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            results = []
            for match in query_response.matches:
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            return results
        except Exception as e:
            print(f"Error searching similar emails: {e}")
            return []
    
    async def upsert_intent_pattern(
        self,
        intent: str,
        embedding: List[float],
        metadata: Dict
    ):
        """Store intent pattern for classification"""
        if self.index is None:
            return
        
        pattern_id = f"intent_{intent}"
        try:
            self.index.upsert(vectors=[{
                "id": pattern_id,
                "values": embedding,
                "metadata": {**metadata, "type": "intent_pattern"}
            }])
        except Exception as e:
            print(f"Error upserting intent pattern: {e}")
    
    async def delete_email(self, email_id: str):
        """Delete email embedding"""
        if self.index is None:
            return
        
        try:
            self.index.delete(ids=[email_id])
        except Exception as e:
            print(f"Error deleting email: {e}")
