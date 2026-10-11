from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class QueryConfig:
    type: str
    fields: Optional[List[str]] = None
    operator: Optional[str] = None
    vector_field: Optional[str] = None
    vector_fields: Optional[List[str]] = None
    query_vector_param: Optional[str] = None
    bm25_fields: Optional[List[str]] = None
    target_hits: int = 10
    # Retrieval operators combined with OR for type="composite": keyword | sparse | dense
    retrieval: Optional[Tuple[str, ...]] = None
    sparse_operator: str = "wand"  # wand | dotProduct
    sparse_top_k: Optional[int] = None  # keep only the k heaviest query tokens
    sparse_query_param: str = "input.query(qs)"
    dense_field: str = "embedding"


@dataclass(frozen=True)
class Strategy:
    id: str
    rank_profile: str
    requires_embedding: bool
    description: str
    query_config: QueryConfig
    requires_sparse: bool = False


STRATEGIES = [
    Strategy(
        id="bm25_title_body",
        rank_profile="bm25_title_body",
        requires_embedding=False,
        description="Sparse BM25 search on title and body.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="bm25_semantic_summary",
        rank_profile="bm25_semantic_summary",
        requires_embedding=False,
        description="Sparse BM25 search on title, body, and semantic summary fields.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body", "summary_text", "semantic_text"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="dense_embedding",
        rank_profile="dense_embedding",
        requires_embedding=True,
        description="Dense embedding search using a single document embedding vector.",
        query_config=QueryConfig(
            type="vector",
            vector_field="embedding",
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="multi_dense",
        rank_profile="multi_dense",
        requires_embedding=True,
        description="Multi-vector semantic search over title and body embeddings.",
        query_config=QueryConfig(
            type="multi_vector",
            vector_fields=["title_embedding", "body_embedding"],
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="hybrid",
        rank_profile="hybrid",
        requires_embedding=True,
        description="Hybrid BM25 + single embedding search.",
        query_config=QueryConfig(
            type="hybrid",
            bm25_fields=["title", "body"],
            vector_field="embedding",
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="hybrid_multi",
        rank_profile="hybrid_multi",
        requires_embedding=True,
        description="Hybrid BM25 + multi-vector search with title/body embeddings.",
        query_config=QueryConfig(
            type="hybrid_multi",
            bm25_fields=["title", "body"],
            vector_fields=["title_embedding", "body_embedding"],
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="bm25_title_body_boosted",
        rank_profile="bm25_title_body_boosted",
        requires_embedding=False,
        description="Field-weighted BM25 search boosting title more strongly.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="bm25_semantic_summary_boosted",
        rank_profile="bm25_semantic_summary_boosted",
        requires_embedding=False,
        description="Field-weighted BM25 over title, body, and semantic fields.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body", "summary_text", "semantic_text"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="bm25_title_body_phrase",
        rank_profile="bm25_title_body_phrase",
        requires_embedding=False,
        description="BM25 title/body retrieval with phrase boosting on title and body.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="bm25_semantic_summary_phrase",
        rank_profile="bm25_semantic_summary_phrase",
        requires_embedding=False,
        description="BM25 retrieval with semantic fields and phrase boosting.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body", "summary_text", "semantic_text"],
            operator="userQuery",
        ),
    ),
    Strategy(
        id="hybrid_semantic_summary",
        rank_profile="hybrid_semantic_summary",
        requires_embedding=True,
        description="Hybrid BM25 and embedding search with additional semantic field weighting.",
        query_config=QueryConfig(
            type="hybrid",
            bm25_fields=["title", "body", "summary_text", "semantic_text"],
            vector_field="embedding",
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="hybrid_multi_weighted",
        rank_profile="hybrid_multi_weighted",
        requires_embedding=True,
        description="Hybrid multi-vector retrieval with a stronger title BM25 signal.",
        query_config=QueryConfig(
            type="hybrid_multi",
            bm25_fields=["title", "body"],
            vector_fields=["title_embedding", "body_embedding"],
            query_vector_param="input.query(q)",
        ),
    ),
    Strategy(
        id="hybrid_rerank",
        rank_profile="hybrid_rerank",
        requires_embedding=True,
        description="Hybrid retrieval with an expensive reranker using phrase boosts.",
        query_config=QueryConfig(
            type="hybrid",
            bm25_fields=["title", "body"],
            vector_field="embedding",
            query_vector_param="input.query(q)",
            target_hits=20,
        ),
    ),
    Strategy(
        id="hybrid_multi_rerank",
        rank_profile="hybrid_multi_rerank",
        requires_embedding=True,
        description="Hybrid multi-vector retrieval with a reranker that emphasizes title phrases.",
        query_config=QueryConfig(
            type="hybrid_multi",
            bm25_fields=["title", "body"],
            vector_fields=["title_embedding", "body_embedding"],
            query_vector_param="input.query(q)",
            target_hits=20,
        ),
    ),
    Strategy(
        id="bm25_title_body_wide",
        rank_profile="bm25_title_body",
        requires_embedding=False,
        description="Wider BM25 candidate pool on title and body.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body"],
            operator="userQuery",
            target_hits=20,
        ),
    ),
    Strategy(
        id="bm25_semantic_summary_wide",
        rank_profile="bm25_semantic_summary",
        requires_embedding=False,
        description="Wider BM25 candidate pool using semantic summary fields.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body", "summary_text", "semantic_text"],
            operator="userQuery",
            target_hits=20,
        ),
    ),
    Strategy(
        id="hybrid_wide",
        rank_profile="hybrid",
        requires_embedding=True,
        description="Hybrid retrieval with a wider candidate pool for stronger reranking potential.",
        query_config=QueryConfig(
            type="hybrid",
            bm25_fields=["title", "body"],
            vector_field="embedding",
            query_vector_param="input.query(q)",
            target_hits=20,
        ),
    ),
    Strategy(
        id="hybrid_multi_wide",
        rank_profile="hybrid_multi",
        requires_embedding=True,
        description="Hybrid multi-vector retrieval with a wider candidate pool.",
        query_config=QueryConfig(
            type="hybrid_multi",
            bm25_fields=["title", "body"],
            vector_fields=["title_embedding", "body_embedding"],
            query_vector_param="input.query(q)",
            target_hits=20,
        ),
    ),
    Strategy(
        id="bm25_title_body_deep",
        rank_profile="bm25_title_body",
        requires_embedding=False,
        description="Deep BM25 retrieval on title and body with a larger candidate set.",
        query_config=QueryConfig(
            type="bm25",
            fields=["title", "body"],
            operator="userQuery",
            target_hits=30,
        ),
    ),
    Strategy(
        id="hybrid_deep",
        rank_profile="hybrid",
        requires_embedding=True,
        description="Deep hybrid retrieval with a larger candidate set for stronger ranking.",
        query_config=QueryConfig(
            type="hybrid",
            bm25_fields=["title", "body"],
            vector_field="embedding",
            query_vector_param="input.query(q)",
            target_hits=30,
        ),
    ),
    Strategy(
        id="sparse_wand",
        rank_profile="sparse_dot",
        requires_embedding=False,
        requires_sparse=True,
        description="BGE-M3 sparse query, WAND retrieval, sparse dot-product ranking.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse',),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_wand_pruned",
        rank_profile="sparse_dot",
        requires_embedding=False,
        requires_sparse=True,
        description="Sparse query pruned to the 6 heaviest tokens before WAND.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse',),
            sparse_operator="wand",
            sparse_top_k=6,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_dotproduct",
        rank_profile="sparse_rawscore",
        requires_embedding=False,
        requires_sparse=True,
        description="Exhaustive dotProduct operator over all query tokens, ranked by rawScore.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse',),
            sparse_operator="dotProduct",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_field_weighted",
        rank_profile="sparse_field_weighted",
        requires_embedding=False,
        requires_sparse=True,
        description="Sparse query with title sparse vector weighted 2x over the full-text sparse vector.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse',),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_retrieve_dense_rank",
        rank_profile="sparse_dense",
        requires_embedding=True,
        requires_sparse=True,
        description="Sparse WAND retrieval, then dense + sparse scoring of the candidates.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse',),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="dense_retrieve_sparse_rank",
        rank_profile="dense_retrieve_sparse_rank",
        requires_embedding=True,
        requires_sparse=True,
        description="ANN retrieval, then candidates re-scored by sparse dot-product.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('dense',),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_dense",
        rank_profile="sparse_dense",
        requires_embedding=True,
        requires_sparse=True,
        description="Union of sparse WAND and dense ANN retrieval, scored dense + 0.3 * sparse.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('sparse', 'dense'),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_keyword",
        rank_profile="sparse_keyword",
        requires_embedding=False,
        requires_sparse=True,
        description="Union of keyword and sparse retrieval, scored sparse + 0.1 * BM25.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('keyword', 'sparse'),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_dense_keyword",
        rank_profile="sparse_dense_keyword",
        requires_embedding=True,
        requires_sparse=True,
        description="Union of keyword, sparse and dense retrieval with a linear score mix.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('keyword', 'sparse', 'dense'),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=10,
        ),
    ),
    Strategy(
        id="sparse_dense_keyword_rerank",
        rank_profile="sparse_dense_keyword_rerank",
        requires_embedding=True,
        requires_sparse=True,
        description="Cheap dense+sparse first phase, BM25 and field-match added in a second-phase rerank.",
        query_config=QueryConfig(
            type="composite",
            retrieval=('keyword', 'sparse', 'dense'),
            sparse_operator="wand",
            sparse_top_k=None,
            target_hits=20,
        ),
    ),
]
