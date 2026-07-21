# Vespa Evaluation Framework

## Purpose

This project provides a lightweight evaluation framework for comparing retrieval and ranking strategies in Vespa. It helps you benchmark approaches such as BM25, dense vector search, multi-vector retrieval, and hybrid lexical + semantic retrieval on a small, reproducible dataset.

The framework can be used to:

- compare retrieval quality across multiple strategies
- evaluate relevance metrics such as precision, recall, nDCG, MRR, and MAP
- generate a human-readable benchmark report
- explore how Vespa performs relative to Elasticsearch for search and ranking workloads

## Project structure

The repository contains:

- `src/` with the evaluation, indexing, embedding, and reporting logic
- `docs/` with supplementary notes on Vespa features and comparisons
- `tests/` with unit tests for the core modules
- sample datasets in `src/vespa_test_dataset.json` and `src/vespa_hard_test_dataset.json`

## How to run the evaluator

### Prerequisites

- Python 3.10+
- a running Vespa application reachable at `http://localhost:8080` by default
- dependencies installed from the project configuration

### Installation

From the project root:

```bash
pip install -e .
```

### Execute the benchmark

For a notebook-based getting-started example, see [the example notebook](https://github.com/egerpaulj/vespa_eval_framework/blob/main/notebooks/getting_started.ipynb).

Run the evaluator from the package source directory:

```bash
cd vespa_eval_framework/src
python vespa_eval_framework.py
```

The script will:

1. load the default dataset
2. connect to Vespa
3. index documents
4. run the configured strategies
5. write a benchmark report to `vespa_benchmark_results.md`

You can also inspect runtime logs in `vespa_eval.log`.

## Test data examples

The framework ships with example datasets that include both documents and relevance-labeled queries. The default dataset is the harder variant, but the simpler example dataset is also available.

### Example documents

The sample documents cover topics such as:

- Vespa search and ranking
- BM25 configuration
- dense embeddings
- hybrid retrieval
- question answering and passage retrieval
- evaluation metrics

### Example queries

Example queries in the bundled data include:

- "What is hybrid search?"
- "How do I configure BM25 in Vespa?"
- "semantic retrieval using embeddings"
- "phrase queries exact match support"
- "How do I bake sourdough bread?"

Each query contains one or more relevant document IDs, which allow the evaluation framework to compute ranking metrics.

## Retrieval strategies

The framework evaluates a broad set of retrieval strategies, including:

- BM25 on title and body
- BM25 over title, body, and semantic fields
- dense embedding search
- multi-vector semantic search
- hybrid BM25 + embedding search
- hybrid multi-vector search
- weighted and phrase-boosted variants
- deeper or wider candidate-pool variants for reranking scenarios

These strategies are defined in `src/strategies.py` and are executed by the benchmark runner.

## Generated report

After a run, the framework writes a Markdown report named `vespa_benchmark_results.md`.

The report includes:

- a summary table of strategy performance
- metric definitions for precision, recall, nDCG, MRR, and MAP
- Mermaid-based comparison charts
- per-strategy query results

Typical metrics included in the report are:

- Precision@10
- Recall@10
- Precision@1
- Precision@3
- Recall@5
- nDCG@10
- MRR
- MAP

## Vespa vs. Elasticsearch

For a deeper comparison, see [docs/vespa_vs_elasticsearch.md](docs/vespa_vs_elasticsearch.md).

Vespa and Elasticsearch both support full-text search, but they emphasize different strengths.

### Elasticsearch strengths

- rich analyzer and token-filter pipelines
- mature aggregation and analytics capabilities
- strong support for custom text-analysis workflows

### Vespa strengths

- native hybrid lexical + vector retrieval
- ranking pipelines that combine sparse and dense signals
- built-in support for multi-stage ranking and ONNX-based reranking
- strong fit for low-latency production recommendation and retrieval systems

### Quick comparison

| Capability | Elasticsearch | Vespa |
| --- | --- | --- |
| Text analysis flexibility | Excellent | Good |
| Hybrid lexical + vector search | Good | Excellent |
| ML / ONNX ranking | Limited | Native |
| Large-scale low-latency retrieval | Good | Excellent |
| Ranking pipeline sophistication | Moderate | Strong |

In short, Elasticsearch is often the better fit when you need highly configurable analyzers and analytics, while Vespa is often the better fit when you need advanced retrieval and ranking pipelines with semantic search and ML integration.

## Notes

The framework is intentionally simple and focused on experimentation. It is a good starting point for benchmarking Vespa retrieval strategies before moving to a larger production setup.
