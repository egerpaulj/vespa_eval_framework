import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from text_utils import normalize_text


def test_normalize_text_basic():
    assert normalize_text("  Hello  WORLD \n") == "hello world"
    # non-string is returned as-is
    assert normalize_text(None) is None
