import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indexing import feed_documents


class FakeApp:
    def __init__(self):
        self.feed_calls = []

    def feed_data_point(self, schema, data_id, fields):
        self.feed_calls.append((schema, data_id, fields.copy()))


class FakeEmbedder:
    def encode(self, inputs):
        # return three embeddings (full, title, body)
        return [[0.1] * 3, [0.2] * 3, [0.3] * 3]


def test_feed_documents_adds_embeddings_and_normalizes():
    app = FakeApp()
    embedder = FakeEmbedder()
    documents = [
        {"id": "doc-1", "title": "  Title CASE ", "body": " Body text "},
    ]

    feed_documents(app, documents, embedder=embedder)

    assert len(app.feed_calls) == 1
    schema, data_id, fields = app.feed_calls[0]
    assert schema == "doc"
    assert data_id == "doc-1"
    assert "embedding" in fields
    assert "title_embedding" in fields
    assert "body_embedding" in fields
    # normalized title/body should be lowercased and stripped
    assert fields["title"] == "title case"
    assert fields["body"] == "body text"
