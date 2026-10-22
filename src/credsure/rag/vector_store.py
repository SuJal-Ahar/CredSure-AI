"""Embedded Qdrant Vector Store with FastEmbed BAAI/bge-small-en-v1.5.

Runs in embedded local disk mode: path="./data/qdrant_storage"
Zero external database server required.
Zero external API keys required for CPU embeddings.
"""

import os
import hashlib
from typing import Dict, List, Any, Optional
import numpy as np


class QdrantPolicyVectorStore:
    """Manages the embedded local Qdrant vector database and CPU embeddings

    for underwriting rule retrieval.
    """

    COLLECTION_NAME = "credit_underwriting_policies"
    VECTOR_DIM = 384  # BAAI/bge-small-en-v1.5 vector dimension

    def __init__(self, storage_path: str = "./data/qdrant_storage"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.client = None
        self.embedding_model = None
        self._init_qdrant()
        self._init_embedder()

    def _init_qdrant(self):
        """Initialize embedded local Qdrant client."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self.client = QdrantClient(path=self.storage_path)

            collections = self.client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(size=self.VECTOR_DIM, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"Notice: Qdrant client initialized in local in-memory fallback: {e}")
            self.client = None

    def _init_embedder(self):
        """Initialize CPU-based FastEmbed model (BAAI/bge-small-en-v1.5)."""
        try:
            from fastembed import TextEmbedding
            self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except Exception as e:
            print(f"Notice: FastEmbed initialization: {e}. Using deterministic semantic hash embeddings.")
            self.embedding_model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate 384-dimensional dense vectors for input texts."""
        if self.embedding_model is not None:
            try:
                embeddings = list(self.embedding_model.embed(texts))
                return [e.tolist() for e in embeddings]
            except Exception as e:
                print(f"FastEmbed runtime error: {e}. Falling back to deterministic dense embeddings.")

        # Resilient offline CPU vectorizer (deterministic normalized pseudo-embeddings)
        vectors = []
        for text in texts:
            words = text.lower().split()
            vec = np.zeros(self.VECTOR_DIM, dtype=np.float32)
            for i, word in enumerate(words):
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = h % self.VECTOR_DIM
                weight = 1.0 / (1.0 + 0.1 * i)
                vec[idx] += weight
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec.tolist())
        return vectors

    def index_policies(self, chunks: List[Dict[str, Any]]) -> int:
        """Embed and upsert policy chunks into the local Qdrant collection."""
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        embeddings = self.embed_texts(texts)

        if self.client is not None:
            try:
                from qdrant_client.models import PointStruct

                points = []
                for i, chunk in enumerate(chunks):
                    point_id = int(hashlib.md5(chunk["id"].encode()).hexdigest()[:8], 16)
                    payload = {
                        "chunk_id": chunk["id"],
                        "section_title": chunk.get("section_title", ""),
                        "rule_category": chunk.get("rule_category", "general"),
                        "min_score": chunk.get("min_score", 0),
                        "text": chunk["text"],
                        "metadata": chunk.get("metadata", {}),
                    }
                    points.append(PointStruct(id=point_id, vector=embeddings[i], payload=payload))

                self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)
                return len(points)
            except Exception as e:
                print(f"Qdrant upsert warning: {e}")

        # In-memory storage cache if Qdrant disk is locked
        self._cached_chunks = chunks
        self._cached_embeddings = embeddings
        return len(chunks)

    def search(
        self,
        query: str,
        limit: int = 3,
        rule_category: Optional[str] = None,
        min_score: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant underwriting policies using vector similarity & metadata filters."""
        query_vector = self.embed_texts([query])[0]

        if self.client is not None:
            try:
                from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

                conditions = []
                if rule_category:
                    conditions.append(FieldCondition(key="rule_category", match=MatchValue(value=rule_category)))
                if min_score is not None:
                    conditions.append(FieldCondition(key="min_score", range=Range(gte=min_score)))

                query_filter = Filter(must=conditions) if conditions else None

                results = self.client.search(
                    collection_name=self.COLLECTION_NAME,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=limit,
                )

                return [
                    {
                        "chunk_id": hit.payload.get("chunk_id", ""),
                        "section_title": hit.payload.get("section_title", ""),
                        "rule_category": hit.payload.get("rule_category", ""),
                        "min_score": hit.payload.get("min_score", 0),
                        "text": hit.payload.get("text", ""),
                        "score": round(float(hit.score), 4),
                        "metadata": hit.payload.get("metadata", {}),
                    }
                    for hit in results
                ]
            except Exception as e:
                print(f"Qdrant search fallback: {e}")

        # Fallback in-memory cosine search
        if hasattr(self, "_cached_chunks") and self._cached_chunks:
            scores = []
            q_arr = np.array(query_vector, dtype=np.float32)
            for i, chunk in enumerate(self._cached_chunks):
                c_vec = np.array(self._cached_embeddings[i], dtype=np.float32)
                sim = float(np.dot(q_arr, c_vec) / (np.linalg.norm(q_arr) * np.linalg.norm(c_vec) + 1e-7))
                if rule_category and chunk.get("rule_category") != rule_category:
                    continue
                scores.append((sim, chunk))
            scores.sort(key=lambda x: x[0], reverse=True)
            return [
                {
                    "chunk_id": s[1]["id"],
                    "section_title": s[1].get("section_title", ""),
                    "rule_category": s[1].get("rule_category", ""),
                    "min_score": s[1].get("min_score", 0),
                    "text": s[1]["text"],
                    "score": round(s[0], 4),
                    "metadata": s[1].get("metadata", {}),
                }
                for s in scores[:limit]
            ]

        return []
