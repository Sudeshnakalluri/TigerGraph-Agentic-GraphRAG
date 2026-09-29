"""CLI runner for Public Benchmark & Hidden Predictions generation."""
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.evaluation.benchmark_runner import BenchmarkRunner

def main():
    parser = argparse.ArgumentParser(description="TigerGraph Agentic GraphRAG Benchmark Runner")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of public evaluation questions (default: all 100)")
    parser.add_argument("--skip-hidden", action="store_true", help="Skip generating 50 hidden question predictions")
    args = parser.parse_args()

    print("=" * 60)
    print("STARTING TIGERGRAPH 3-WAY BENCHMARK RUNNER")
    print("=" * 60)

    runner = BenchmarkRunner()
    results = runner.run_public_benchmark(sample_limit=args.limit)
    print(f"\nEvaluated {results['total_questions_evaluated']} questions.")
    print(f"Overall Agent Necessity Rate: {results['overall_agent_necessity_rate'] * 100:.1f}%")

    if not args.skip_hidden:
        print("\nGenerating submission file for 50 hidden questions...")
        sub_path = runner.generate_hidden_submission()
        print(f"Submission generated at: {sub_path}")

    print("\nBenchmark completed successfully!")

if __name__ == "__main__":
    main()
