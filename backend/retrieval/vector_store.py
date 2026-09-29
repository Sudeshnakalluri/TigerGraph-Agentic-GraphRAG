"""FAISS Vector Store and Embeddings Engine for Dense Retrieval."""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from config.settings import (
    CORPUS_FILE,
    FAISS_INDEX_FILE,
    CHUNKS_FILE,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIM,
    TOP_K
)

class VectorStore:
    """FAISS-based dense semantic retriever over corpus articles."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []
        self.dim = EMBEDDING_DIM

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def load_or_build(self, force_rebuild: bool = False):
        """Loads FAISS index from disk, or builds from corpus.jsonl if not found."""
        if not force_rebuild and FAISS_INDEX_FILE.exists() and CHUNKS_FILE.exists():
            self.load()
        else:
            self.build_from_corpus()

    def load(self):
        """Loads FAISS index and chunk metadata from disk."""
        print(f"Loading FAISS index from {FAISS_INDEX_FILE}...")
        self.index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        print(f"Loaded {len(self.chunks)} chunks into FAISS index.")

    def save(self):
        """Saves FAISS index and chunks to disk."""
        FAISS_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(FAISS_INDEX_FILE))
        with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False)
        print(f"Saved FAISS index ({self.index.ntotal} vectors) to {FAISS_INDEX_FILE}")

    def build_from_corpus(self, max_docs: Optional[int] = None):
        """Extracts text passages from corpus.jsonl, embeds them, and creates FAISS index."""
        print("Building vector index from corpus.jsonl...")
        self._load_model()
        chunks = []
        texts = []

        with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
            count = 0
            for line in f:
                if not line.strip():
                    continue
                doc = json.loads(line)
                count += 1
                if max_docs and count > max_docs:
                    break

                doc_id = doc.get("doc_id", f"doc_{count}")
                title = doc.get("title", "")
                text = doc.get("text", "")
                url = doc.get("url", "")

                # Split text into paragraphs
                paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 60]
                if not paragraphs:
                    paragraphs = [text[:1000]]

                for p_idx, para in enumerate(paragraphs[:4]): # up to 4 key passages per doc
                    chunk_id = f"{doc_id}_p{p_idx}"
                    chunk_text = f"{title}\n{para}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "title": title,
                        "url": url,
                        "text": chunk_text
                    })
                    texts.append(chunk_text)

        print(f"Embedding {len(texts)} chunks using {self.model_name}...")
        embeddings = self.model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)

        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(embeddings)
        self.chunks = chunks
        self.save()

    def search(self, query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """Performs cosine similarity search against index."""
        if self.index is None or not self.chunks:
            self.load_or_build()
        self._load_model()

        q_vec = self.model.encode([query], normalize_embeddings=True)
        q_vec = np.array(q_vec, dtype=np.float32)

        scores, indices = self.index.search(q_vec, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(score)
                results.append(chunk)
        return results