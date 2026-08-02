import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import importlib

import pytest

embeddings = importlib.import_module("embeddings")


def test_create_embedder_raises_when_no_backend(monkeypatch):
    monkeypatch.setattr(embeddings, "BGEM3FlagModel", None)
    monkeypatch.setattr(embeddings, "SentenceTransformer", None)
    with pytest.raises(RuntimeError):
        embeddings.create_embedder()
