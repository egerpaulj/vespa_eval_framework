import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluation import normalize_doc_id, average_precision, _dcg


def test_normalize_doc_id_variants():
    assert normalize_doc_id(None) is None
    assert normalize_doc_id("id:doc-1") == "doc-1"
    assert normalize_doc_id("ns::doc-2") == "doc-2"
    assert normalize_doc_id("plain-id") == "plain-id"


def test_average_precision_and_dcg():
    hits = [1, 0, 1, 1]
    ap = average_precision(hits, 3)
    assert ap > 0
    # dcg of simple scores
    scores = [1.0, 0.5, 0.0]
    assert _dcg(scores, 3) > 0
