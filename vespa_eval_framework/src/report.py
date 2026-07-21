import logging
from pathlib import Path
from typing import Dict, List

try:
    import plotly.express as px  # noqa: F401
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)


def pretty_print_query(yql: str, query_text: str, rank_profile: str, target_hits: int, body: Dict) -> str:
    lines = [
        "Query Details:",
        f"  YQL: {yql}",
        f"  Query Text: '{query_text}'",
        f"  Rank Profile: {rank_profile}",
        f"  Target Hits: {target_hits}",
    ]
    if body:
        lines.append(f"  Body Parameters: {list(body.keys())}")
    return "\n".join(lines)


def pretty_print_response(response) -> str:
    lines = ["Response Details:"]
    if hasattr(response, "hits"):
        lines.append(f"  Total Hits: {len(response.hits)}")
        for idx, hit in enumerate(response.hits, start=1):
            if isinstance(hit, dict):
                hit_id = hit.get("id", "unknown")
                score = hit.get("score", "n/a")
            else:
                hit_id = getattr(hit, "id", "unknown")
                score = getattr(hit, "score", "n/a")
            lines.append(f"    [{idx}] ID: {hit_id}, Score: {score}")
    return "\n".join(lines)


def sanitize_for_mermaid(text: str) -> str:
    import re
    text = re.sub(r'[@\-\(\)\[\]{}<>|&*#!.,;:]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_') or "unknown"


def calculate_mermaid_y_axis_range(values: List[float]) -> str:
    if not values:
        return "0 --> 1"

    numeric_values = [float(value) for value in values]
    min_value = min(numeric_values)
    max_value = max(numeric_values)

    if max_value >= 0.95:
        padding = 0.034
        lower = max(0.0, min_value - padding)
        upper = 1.0
    else:
        padding = 0.02
        lower = max(0.0, min_value - padding)
        upper = min(1.0, max_value + padding)

    if upper == lower:
        upper = min(1.0, lower + 0.02)

    return f"{lower:.3f} --> {upper:.3f}"


def generate_mermaid_bar_chart(strategies: List[str], values: List[float], title: str, metric_name: str) -> str:
    sanitized_strategies = [sanitize_for_mermaid(strategy) for strategy in strategies]
    formatted_values = [f"{value:.3f}" for value in values]
    quoted_strategies = [f'"{value}"' for value in sanitized_strategies]

    chart_lines = [
        "```mermaid",
        "---",
        "config:",
        "    xyChart:",
        "        width: 900",
        "        height: 600",
        "    themeVariables:",
        "        xyChart:",
        "            plotColorPalette: \"#2196F3\"",
        "---",
        "xychart-beta",
        f"    title {title}",
        f"    x-axis [{', '.join(quoted_strategies)}]",
        f"    y-axis \"{metric_name}\" {calculate_mermaid_y_axis_range(values)}",
        f"    line [{', '.join(formatted_values)}]",
        "```",
    ]

    return "\n".join(chart_lines)


def generate_summary_report(benchmark_results: Dict, dataset: Dict, output_file: str = "vespa_benchmark_results.md") -> str:
    summary = benchmark_results["summary"]
    query_details = benchmark_results["query_details"]
    output_dir = Path(output_file).parent
    graphs_dir = output_dir / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Vespa Evaluation Framework - Benchmark Results",
        "",
        f"**Dataset**: {len(dataset['documents'])} documents, {len(dataset['queries'])} queries",
        "",
        "## Summary Results Table",
        "",
        "| Strategy | Description | Precision@10 | Recall@10 | Precision@1 | Precision@3 | Recall@5 | nDCG@10 | MRR | MAP |",
        "|----------|-------------|--------------|-----------|-------------|-------------|----------|---------|-----|-----|",
    ]

    for row in summary:
        lines.append(
            f"| {row['strategy']} | {row['description']} | "
            f"{row['avg_precision@10']:.3f} | {row['avg_recall@10']:.3f} | "
            f"{row.get('avg_precision@1', 0.0):.3f} | {row.get('avg_precision@3', 0.0):.3f} | "
            f"{row.get('avg_recall@5', 0.0):.3f} | {row.get('avg_ndcg@10', 0.0):.3f} | "
            f"{row['avg_mrr']:.3f} | {row['avg_map']:.3f} |"
        )

    lines.append("")
    lines.extend([
        "## Metric Glossary",
        "",
        "| Metric | Brief explanation | What it signifies |",
        "|--------|-------------------|-------------------|",
        "| Precision@10 | Share of the top 10 results that are relevant. | Higher values mean the retrieval system is surfacing relevant items near the top of the list. |",
        "| Recall@10 | Fraction of all relevant documents retrieved within the top 10 results. | Higher values mean the system finds more of the relevant documents overall. |",
        "| Precision@1 | Whether the first result is relevant. | This highlights how often the top-ranked result is a strong hit. |",
        "| Precision@3 | Share of the top 3 results that are relevant. | This captures early precision for a short, highly visible result set. |",
        "| Recall@5 | Fraction of relevant documents retrieved in the top 5 results. | This shows how well the system covers relevant results in a compact shortlist. |",
        "| nDCG@10 | Ranking quality that rewards relevant results appearing earlier. | Higher values indicate better ordering of relevant results within the top 10. |",
        "| MRR | Reciprocal rank of the first relevant result. | Higher values mean the first relevant result appears earlier in the ranking. |",
        "| MAP | Mean of average precision across queries. | Higher values mean the system ranks relevant documents consistently well across many queries. |",
        "",
    ])

    strategy_labels = [row["strategy"] for row in summary]
    lines.extend([
        "## Appendix: Metric Comparison Charts",
        "",
        "### Precision@10",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row["avg_precision@10"] for row in summary], "Precision At 10 by Strategy", "Precision"),
        "",
        "### Recall@10",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row["avg_recall@10"] for row in summary], "Recall At 10 by Strategy", "Recall"),
        "",
        "### Precision@1",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row.get("avg_precision@1", 0.0) for row in summary], "Precision At 1 by Strategy", "Precision"),
        "",
        "### Precision@3",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row.get("avg_precision@3", 0.0) for row in summary], "Precision At 3 by Strategy", "Precision"),
        "",
        "### Recall@5",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row.get("avg_recall@5", 0.0) for row in summary], "Recall At 5 by Strategy", "Recall"),
        "",
        "### nDCG@10",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row.get("avg_ndcg@10", 0.0) for row in summary], "nDCG At 10 by Strategy", "nDCG"),
        "",
        "### Mean Reciprocal Rank (MRR)",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row["avg_mrr"] for row in summary], "MRR by Strategy", "MRR"),
        "",
        "### Mean Average Precision (MAP)",
        "",
        generate_mermaid_bar_chart(strategy_labels, [row["avg_map"] for row in summary], "MAP by Strategy", "MAP"),
        "",
    ])

    lines.extend(["## Per-Strategy Query Results", ""])
    for strategy_id, queries in query_details.items():
        lines.extend([
            f"### {strategy_id}",
            "",
            "| Query | Precision@10 | Recall@10 | Precision@1 | Precision@3 | Recall@5 | nDCG@10 | MRR | MAP |",
            "|-------|--------------|-----------|-------------|-------------|----------|---------|-----|-----|",
        ])
        for query in queries:
            lines.append(
                f"| {query['query_text'][:50]}... | {query['precision@10']:.3f} | {query['recall@10']:.3f} | "
                f"{query.get('precision@1', 0.0):.3f} | {query.get('precision@3', 0.0):.3f} | "
                f"{query.get('recall@5', 0.0):.3f} | {query.get('ndcg@10', 0.0):.3f} | "
                f"{query['mrr']:.3f} | {query['map']:.3f} |"
            )
        lines.append("")

    content = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(content)
    logger.info(f"Summary report written to {output_file}")
    return content
