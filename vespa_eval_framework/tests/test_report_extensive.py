import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from report import (
    pretty_print_query,
    pretty_print_response,
    sanitize_for_mermaid,
    calculate_mermaid_y_axis_range,
    generate_mermaid_bar_chart,
)


def test_pretty_print_query_includes_body_keys():
    yql = "select * from doc where userQuery()"
    query_text = "Find this"
    body = {"input.query(q)": [0.1, 0.2]}

    out = pretty_print_query(yql, query_text, "default", 10, body)
    assert "YQL: select * from doc where userQuery()" in out
    assert "Query Text: 'Find this'" in out
    assert "Body Parameters: ['input.query(q)']" in out


def test_pretty_print_response_with_dict_and_obj_hits():
    class HitObj:
        def __init__(self, id, score):
            self.id = id
            self.score = score

    response = type("R", (), {})()
    response.hits = [
        {"id": "doc-1", "score": 0.5},
        HitObj("doc-2", 0.8),
    ]

    out = pretty_print_response(response)
    assert "Total Hits: 2" in out
    assert "ID: doc-1" in out
    assert "ID: doc-2" in out


def test_sanitize_for_mermaid_replaces_special_chars():
    assert sanitize_for_mermaid("a@b-c(d)[e]{f}<g>|h&i*j#.,;:") == "a_b_c_d_e_f_g_h_i_j"
    assert sanitize_for_mermaid("") == "unknown"


def test_calculate_mermaid_y_axis_range_empty():
    assert calculate_mermaid_y_axis_range([]) == "0 --> 1"


def test_calculate_mermaid_y_axis_range_small_values():
    rng = calculate_mermaid_y_axis_range([0.1, 0.12, 0.09])
    assert "-->" in rng
    lower, upper = rng.split("-->")
    assert float(lower) < float(upper)


def test_calculate_mermaid_y_axis_range_near_one():
    rng = calculate_mermaid_y_axis_range([0.96, 1.0, 0.95])
    assert rng.endswith("--> 1.000")


def test_generate_mermaid_bar_chart_contains_expected_blocks():
    chart = generate_mermaid_bar_chart(["s1", "s2"], [0.1, 0.2], "Title", "Precision")
    assert "```mermaid" in chart
    assert "xychart-beta" in chart
    assert 'y-axis "Precision"' in chart
    assert "line [0.100, 0.200]" in chart
