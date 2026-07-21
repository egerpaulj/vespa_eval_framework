import json
import logging
import random
from pathlib import Path
from typing import Dict, List

from constants import DATA_FILE, NEGATIVE_SAMPLES_PER_QUERY

logger = logging.getLogger(__name__)


def load_dataset(path: Path = DATA_FILE) -> Dict[str, List[Dict]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    documents = data.get("documents", [])
    doc_ids = [doc.get("id") for doc in documents if "id" in doc]
    changed = False

    for query in data.get("queries", []):
        relevant_ids = set(query.get("relevant_ids", []))
        if "negative_ids" not in query:
            negatives = [doc_id for doc_id in doc_ids if doc_id not in relevant_ids]
            sample_size = min(len(negatives), NEGATIVE_SAMPLES_PER_QUERY)
            query["negative_ids"] = random.sample(negatives, sample_size) if sample_size > 0 else []
            changed = True

    if changed:
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            logger.info(f"Persisted negative samples to dataset file: {path}")
        except Exception as exc:
            logger.error(f"Failed to persist negatives to {path}: {exc}")

    return data
