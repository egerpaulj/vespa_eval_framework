import logging

from data import load_dataset
from embeddings import create_embedder
from evaluation import BenchmarkRunner
from indexing import feed_documents
from report import generate_summary_report
from strategies import STRATEGIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vespa_eval.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def create_vespa_application(url: str = "http://localhost", port: int = 8080):
    from vespa.application import Vespa

    return Vespa(url=url, port=port)


def main() -> None:
    logger.info("=" * 80)
    logger.info("Vespa Evaluation Framework Starting")
    logger.info("=" * 80)

    dataset = load_dataset()
    logger.info(
        "Loaded dataset with %d documents and %d queries",
        len(dataset["documents"]),
        len(dataset["queries"]),
    )

    app = create_vespa_application()
    logger.info("Connected to Vespa application")

    embedder = create_embedder() if any(strategy.requires_embedding for strategy in STRATEGIES) else None
    if embedder is not None:
        logger.info("Initialized embedder")
    else:
        logger.info("No embedder required for selected strategies")

    logger.info("\nPhase 1: Indexing documents into Vespa...")
    feed_documents(app, dataset["documents"], embedder=embedder)

    logger.info("\nPhase 2: Evaluating strategies...")
    benchmark_runner = BenchmarkRunner(app, embedder=embedder)
    benchmark_results = benchmark_runner.benchmark_strategies(STRATEGIES, dataset)

    logger.info("\n" + "=" * 80)
    logger.info("Strategy benchmark results:")
    logger.info("=" * 80)
    for row in benchmark_results["summary"]:
        result_line = (
            f"{row['strategy']}: precision@10={row['avg_precision@10']:.3f}, "
            f"recall@10={row['avg_recall@10']:.3f}, precision@1={row['avg_precision@1']:.3f}, "
            f"precision@3={row['avg_precision@3']:.3f}, recall@5={row['avg_recall@5']:.3f}, "
            f"ndcg@10={row['avg_ndcg@10']:.3f}, mrr={row['avg_mrr']:.3f}, map={row['avg_map']:.3f}"
        )
        logger.info(result_line)
        print(result_line)
    logger.info("=" * 80)

    logger.info("\nPhase 3: Generating summary report...")
    generate_summary_report(benchmark_results, dataset, output_file="vespa_benchmark_results.md")
    logger.info("Summary report generated: vespa_benchmark_results.md")
    logger.info("Benchmark completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("Error during benchmark: %s", exc, exc_info=True)
        raise
