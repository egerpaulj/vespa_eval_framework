import logging
import math
from typing import Dict, List, Optional
from vespa.application import Vespa

from report import pretty_print_query, pretty_print_response
from strategies import Strategy
from text_utils import normalize_text

logger = logging.getLogger(__name__)


def normalize_doc_id(doc_id: Optional[str]) -> Optional[str]:
    if not isinstance(doc_id, str):
        return doc_id

    if "::" in doc_id:
        return doc_id.split("::")[-1]

    if doc_id.startswith("id:"):
        return doc_id.removeprefix("id:")

    return doc_id


def average_precision(hits: List[int], relevant_count: int) -> float:
    if relevant_count == 0:
        return 0.0

    score = 0.0
    relevant_seen = 0
    for index, hit in enumerate(hits, start=1):
        if hit:
            relevant_seen += 1
            score += relevant_seen / index
    return score / relevant_count


def _normalize_relevance_scores(relevance_scores: Optional[Dict[str, float]]) -> Dict[str, float]:
    if not relevance_scores:
        return {}

    normalized_scores = {}
    for doc_id, score in relevance_scores.items():
        normalized_doc_id = normalize_doc_id(doc_id)
        if normalized_doc_id is None:
            continue
        normalized_scores[normalized_doc_id] = float(score)
    return normalized_scores


def _score_for_doc(doc_id: str, relevance_scores: Dict[str, float], relevant_set: set) -> float:
    if doc_id in relevance_scores:
        return relevance_scores[doc_id]
    return 1.0 if doc_id in relevant_set else 0.0


def _dcg(scores: List[float], k: int) -> float:
    dcg = 0.0
    for index, score in enumerate(scores[:k], start=1):
        if score <= 0:
            continue
        dcg += score / math.log2(index + 1)
    return dcg


def evaluate_hits(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int = 10,
    relevance_scores: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    # Normalize document IDs before evaluation. Example: "namespace::id:123" -> "id:123".
    normalized_retrieved_ids = [normalize_doc_id(doc_id) for doc_id in retrieved_ids[:k]]

    # Normalize all relevant doc IDs the same way so matching between retrieved and relevant IDs is consistent.
    normalized_relevant_ids = [normalize_doc_id(doc_id) for doc_id in relevant_ids]

    # Build a unique set of relevant IDs, ignoring any None values produced during normalization.
    relevant_set = {doc_id for doc_id in normalized_relevant_ids if doc_id is not None}

    # Convert relevance scores using normalized document IDs, e.g. {"namespace::id:123": 2} -> {"id:123": 2.0}.
    normalized_relevance_scores = _normalize_relevance_scores(relevance_scores)

    # Create a binary hit list where each retrieved doc is marked as 1 if it is relevant.
    hits = [1 if _score_for_doc(doc_id, normalized_relevance_scores, relevant_set) > 0 else 0 for doc_id in normalized_retrieved_ids]
     
     # count of relevant docs with positive relevance
    num_relevant = sum(1 for doc_id in relevant_set if _score_for_doc(doc_id, normalized_relevance_scores, relevant_set) > 0) 
    
    # number of retrieved docs that are relevant
    true_positives = sum(hits)  

    precision = true_positives / len(hits) if hits else 0.0  
    recall = true_positives / num_relevant if num_relevant else 0.0  

    # reciprocal rank: first relevant result position
    rr = next((1.0 / (idx + 1) for idx, hit in enumerate(hits) if hit), 0.0)  

    ap = average_precision(hits, num_relevant)  # average precision for the ranked list

    precision_at_1 = sum(1 for doc_id in normalized_retrieved_ids[:1] if _score_for_doc(doc_id, normalized_relevance_scores, relevant_set) > 0) / 1 if normalized_retrieved_ids[:1] else 0.0  
    precision_at_3 = sum(1 for doc_id in normalized_retrieved_ids[:3] if _score_for_doc(doc_id, normalized_relevance_scores, relevant_set) > 0) / min(3, len(normalized_retrieved_ids)) if normalized_retrieved_ids else 0.0  
    recall_at_5 = sum(1 for doc_id in normalized_retrieved_ids[:5] if _score_for_doc(doc_id, normalized_relevance_scores, relevant_set) > 0) / num_relevant if num_relevant else 0.0  
    
    # relevance scores for retrieved docs in order
    retrieved_scores = [_score_for_doc(doc_id, normalized_relevance_scores, relevant_set) for doc_id in normalized_retrieved_ids]  
    
    # ideal ranked list of relevance scores for all relevant docs
    ideal_scores = sorted(
        [_score_for_doc(doc_id, normalized_relevance_scores, relevant_set) for doc_id in relevant_set],
        reverse=True,
    )  
    
    # normalized DCG at 10, 0 if ideal DCG is 0
    ndcg_at_10 = _dcg(retrieved_scores, 10) / _dcg(ideal_scores, 10) if _dcg(ideal_scores, 10) > 0 else 0.0  

    return {
        "precision@10": precision,
        "recall@10": recall,
        "precision@1": precision_at_1,
        "precision@3": precision_at_3,
        "recall@5": recall_at_5,
        "ndcg@10": ndcg_at_10,
        "mrr": rr,
        "average_precision": ap,
    }


class QueryExecutor:
    def __init__(self, app: Vespa, target_hits: int = 10):
        self.app = app
        self.target_hits = target_hits

    def _build_query(self, strategy: Strategy, normalized_query: str, body: Dict) -> tuple[str, Dict]:
        query_config = strategy.query_config
        query_type = query_config.type

        if strategy.requires_embedding:
            if body.get("input.query(q)") is None:
                raise RuntimeError("Embedding model is required for this strategy.")

        if query_type == "bm25":
            yql = "select * from doc where userQuery()"
        elif query_type in {"vector", "multi_vector"}:
            ann_fields = query_config.vector_fields or [query_config.vector_field]
            ann_predicates = [
                f'([{{"targetHits": {self.target_hits}}}]nearestNeighbor({field}, q))'
                for field in ann_fields
                if field
            ]
            yql = f"select * from doc where {' or '.join(ann_predicates)}"
        elif query_type in {"hybrid", "hybrid_multi"}:
            ann_fields = query_config.vector_fields or [query_config.vector_field]
            ann_predicates = [
                f'([{{"targetHits": {self.target_hits}}}]nearestNeighbor({field}, q))'
                for field in ann_fields
                if field
            ]
            yql = f"select * from doc where userQuery() or {' or '.join(ann_predicates)}"
        else:
            yql = "select * from doc where userQuery()"

        return yql, body

    def run_query(
        self,
        strategy: Strategy,
        query_text: str,
        embedder: Optional[object] = None,
    ) -> List[str]:
        normalized_query = normalize_text(query_text)
        body = {}
        query_config = strategy.query_config
        query_type = query_config.type

        if strategy.requires_embedding:
            if embedder is None:
                raise RuntimeError("Embedding model is required for this strategy.")
            query_vector = embedder.encode([normalized_query])[0]
            body[query_config.query_vector_param or "input.query(q)"] = query_vector

        target_hits = query_config.target_hits or self.target_hits
        yql, body = self._build_query(strategy, normalized_query, body)

        logger.info(
            "Strategy: %s\n%s",
            strategy.id,
            pretty_print_query(yql, normalized_query, strategy.rank_profile, target_hits, body),
        )

        response = self.app.query(
            yql=yql,
            query=normalized_query,
            ranking=strategy.rank_profile,
            hits=target_hits,
            body=body,
        )

        hits_list = getattr(response, "hits", []) or []
        result_ids = []
        for hit in hits_list:
            if isinstance(hit, dict):
                raw_doc_id = hit.get("id")
            else:
                raw_doc_id = getattr(hit, "id", None)
            normalized_doc_id = normalize_doc_id(raw_doc_id)
            if normalized_doc_id is not None:
                result_ids.append(normalized_doc_id)

        logger.debug("%s", pretty_print_response(response))
        if not result_ids:
            logger.warning(
                "No hits returned for query '%s' (strategy=%s).",
                query_text,
                strategy.id,
            )

        return result_ids


class BenchmarkRunner:
    def __init__(self, app: Vespa, embedder: Optional[object] = None, target_hits: int = 10):
        self.executor = QueryExecutor(app, target_hits=target_hits)
        self.embedder = embedder

    def benchmark_strategies(self, strategies: List[Strategy], dataset: Dict) -> Dict:
        summary = []
        query_details = {}

        for strategy in strategies:
            query_results = []
            metrics_for_strategy = []
            for query in dataset["queries"]:
                retrieved_ids = self.executor.run_query(
                    strategy,
                    query["text"],
                    self.embedder,
                )
                relevance_scores = query.get("relevance_scores")
                metrics = evaluate_hits(
                    retrieved_ids,
                    query["relevant_ids"],
                    relevance_scores=relevance_scores,
                )
                metrics_for_strategy.append(metrics)
                query_results.append(
                    {
                        "query_text": query["text"],
                        "precision@10": metrics["precision@10"],
                        "recall@10": metrics["recall@10"],
                        "precision@1": metrics["precision@1"],
                        "precision@3": metrics["precision@3"],
                        "recall@5": metrics["recall@5"],
                        "ndcg@10": metrics["ndcg@10"],
                        "mrr": metrics["mrr"],
                        "map": metrics["average_precision"],
                    }
                )

            summary.append(
                {
                    "strategy": strategy.id,
                    "description": strategy.description,
                    "avg_precision@10": sum(m["precision@10"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_recall@10": sum(m["recall@10"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_precision@1": sum(m["precision@1"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_precision@3": sum(m["precision@3"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_recall@5": sum(m["recall@5"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_ndcg@10": sum(m["ndcg@10"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_mrr": sum(m["mrr"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                    "avg_map": sum(m["average_precision"] for m in metrics_for_strategy) / len(metrics_for_strategy),
                }
            )
            query_details[strategy.id] = query_results

        return {"summary": summary, "query_details": query_details}
