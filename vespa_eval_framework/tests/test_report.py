from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from report import generate_summary_report


def test_generate_summary_report_adds_metric_notes_and_scaled_mermaid_charts(tmp_path):
    benchmark_results = {
        "summary": [
            {
                "strategy": "dense_embedding",
                "description": "Dense embedding search",
                "avg_precision@10": 0.108,
                "avg_recall@10": 1.0,
                "avg_mrr": 0.958,
                "avg_map": 0.958,
            }
        ],
        "query_details": {"dense_embedding": []},
    }
    dataset = {"documents": [{"id": "doc-1"}], "queries": [{"id": "q-1"}]}
    output_file = tmp_path / "benchmark_report.md"

    content = generate_summary_report(benchmark_results, dataset, output_file=str(output_file))

    assert "| Metric | Brief explanation | What it signifies |" in content
    assert "| Precision@10 |" in content
    assert "| MRR |" in content
    assert "| MAP |" in content
    assert "## Appendix: Metric Comparison Charts" in content
    assert "### Precision@10" in content
    assert "### Recall@10" in content
    assert "### Mean Reciprocal Rank (MRR)" in content
    assert "### Mean Average Precision (MAP)" in content
    assert 'y-axis "Precision" 0.088 --> 0.128' in content
    assert 'y-axis "MRR" 0.924 --> 1.000' in content
    assert output_file.exists()
