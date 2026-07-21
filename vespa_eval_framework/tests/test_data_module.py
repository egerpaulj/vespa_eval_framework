import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data import load_dataset


def test_load_dataset_persists_negatives(tmp_path):
    data = {
        "documents": [{"id": "d1"}, {"id": "d2"}, {"id": "d3"}],
        "queries": [
            {"id": "q1", "relevant_ids": ["d1"]},
            {"id": "q2", "relevant_ids": []},
        ],
    }
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(data, ensure_ascii=False))

    loaded = load_dataset(path)
    assert "negative_ids" in loaded["queries"][0]
    assert isinstance(loaded["queries"][0]["negative_ids"], list)
    # file should be updated on disk
    reloaded = json.loads(path.read_text())
    assert "negative_ids" in reloaded["queries"][0]


def test_dataset_contains_harder_queries():
    loaded = load_dataset()
    query_ids = {query["id"] for query in loaded["queries"]}

    assert "q25" in query_ids
    assert "q26" in query_ids
    assert "q27" in query_ids
