import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluation import QueryExecutor, evaluate_hits
from strategies import QueryConfig, Strategy, STRATEGIES


def test_evaluate_hits_normalizes_vespa_style_ids():
    retrieved_ids = ["id:doc:doc::doc-002", "id:doc:doc::doc-999"]
    relevant_ids = ["doc-002"]

    metrics = evaluate_hits(retrieved_ids, relevant_ids)

    assert metrics["precision@10"] == 0.5
    assert metrics["recall@10"] == 1.0
    assert metrics["mrr"] == 1.0


def test_evaluate_hits_reports_additional_rank_metrics():
    retrieved_ids = ["doc-002", "doc-001", "doc-999"]
    relevant_ids = ["doc-001", "doc-002"]
    relevance_scores = {"doc-001": 1.0, "doc-002": 1.0}

    metrics = evaluate_hits(retrieved_ids, relevant_ids, relevance_scores=relevance_scores)

    assert metrics["precision@1"] == 1.0
    assert metrics["precision@3"] == pytest.approx(2.0 / 3.0)
    assert metrics["recall@5"] == 1.0
    assert metrics["ndcg@10"] == pytest.approx(1.0)


def test_query_executor_uses_per_strategy_target_hits():
    class FakeApp:
        def __init__(self):
            self.calls = []

        def query(self, **kwargs):
            self.calls.append(kwargs)
            return type("Response", (), {"hits": [{"id": "doc-001"}]})()

    app = FakeApp()
    executor = QueryExecutor(app)
    strategy = Strategy(
        id="bm25_title_body_wide",
        rank_profile="bm25_title_body",
        requires_embedding=False,
        description="Wide candidate BM25",
        query_config=QueryConfig(type="bm25", fields=["title", "body"], target_hits=20),
    )

    executor.run_query(strategy, "test query")

    assert app.calls[0]["hits"] == 20


def test_new_rank_profiles_are_registered():
    ids = {strategy.id for strategy in STRATEGIES}
    assert "bm25_title_body_phrase" in ids
    assert "bm25_semantic_summary_phrase" in ids
    assert "hybrid_rerank" in ids
    assert "hybrid_multi_rerank" in ids
