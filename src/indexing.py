import logging
from typing import Dict, List, Optional

from vespa.application import Vespa

from constants import SPARSE_SCALE
from text_utils import normalize_text

logger = logging.getLogger(__name__)


def feed_documents(app: Vespa, documents: List[Dict], embedder: Optional[object] = None) -> None:
    logger.info("Starting to feed %d documents...", len(documents))

    for idx, doc in enumerate(documents, start=1):
        for field in ("title", "body", "summary_text", "semantic_text"):
            if field in doc and isinstance(doc[field], str):
                doc[field] = normalize_text(doc[field])

        if embedder is not None:
            if "embedding" not in doc or "title_embedding" not in doc or "body_embedding" not in doc:
                model_inputs = [f"{doc['title']} {doc['body']}", doc["title"], doc["body"]]
                full_embedding, title_embedding, body_embedding = embedder.encode(model_inputs)
                doc["embedding"] = full_embedding
                doc["title_embedding"] = title_embedding
                doc["body_embedding"] = body_embedding

        if embedder is not None and getattr(embedder, "supports_sparse", False) and "sparse_tokens" not in doc:
            full_sparse, title_sparse = embedder.encode_sparse([f"{doc['title']} {doc['body']}", doc["title"]])
            doc["sparse_embedding"] = {"cells": full_sparse}
            doc["title_sparse"] = {"cells": title_sparse}
            doc["sparse_tokens"] = {
                token: max(1, int(round(weight * SPARSE_SCALE))) for token, weight in full_sparse.items()
            }

        app.feed_data_point(schema="doc", data_id=doc["id"], fields=doc)
        if idx % 5 == 0:
            logger.debug("Fed %d/%d documents", idx, len(documents))

    logger.info("Successfully fed all %d documents", len(documents))
