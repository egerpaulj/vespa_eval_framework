from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "vespa_hard_test_dataset.json"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
NEGATIVE_SAMPLES_PER_QUERY = 5
