import logging
from abc import ABC, abstractmethod
from typing import List

from constants import DEFAULT_EMBEDDING_MODEL


logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from FlagEmbedding import BGEM3FlagModel
except ImportError:
    BGEM3FlagModel = None


class Embedder(ABC):
    @abstractmethod
    def encode(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def encode_triplet(self, title: str, body: str) -> List[List[float]]:
        return self.encode([f"{title} {body}", title, body])


class BGEM3Embedder(Embedder):
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = BGEM3FlagModel(model_name)
        self.provider = "flag"

    def encode(self, texts: List[str]) -> List[List[float]]:
        vector_data = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )["dense_vecs"]
        return [vec.tolist() for vec in vector_data]


class SentenceTransformersEmbedder(Embedder):
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.provider = "sentence-transformers"

    def encode(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=False).tolist()


def create_embedder(model_name: str = DEFAULT_EMBEDDING_MODEL) -> Embedder:
    if BGEM3FlagModel is not None:
        logger.info("Using BGEM3FlagModel backend for embeddings")
        return BGEM3Embedder("BAAI/bge-m3")
    if SentenceTransformer is not None:
        logger.info("Using SentenceTransformer backend for embeddings")
        return SentenceTransformersEmbedder(model_name)
    raise RuntimeError(
        "No embedding backend is available. Install sentence-transformers or FlagEmbedding."
    )
