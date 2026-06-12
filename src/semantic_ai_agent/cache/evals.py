"""
Cache evaluation utilities for measuring performance and effectiveness.

This module provides tools for:
- Evaluating cache precision, recall, and F1 scores
- Tracking latency and performance metrics
- Calculating cost savings from cache hits
"""

import time
from typing import Any

import numpy as np
import pandas as pd
import tiktoken

from semantic_ai_agent.domain.cache_result import CacheResults


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for
        model: Model name for encoding selection

    Returns:
        Number of tokens
    """
    model_encodings = {
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
    }

    encoding_name = "o200k_base"
    for model_prefix, enc in model_encodings.items():
        if model_prefix in model.lower():
            encoding_name = enc
            break

    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def get_model_cost(provider: str, model: str) -> dict[str, float]:
    """
    Get cost per 1K tokens for a model.

    Returns:
        Dict with "input" and "output" costs per 1K tokens.
    """
    costs = {
        "openai": {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }
    }

    if provider in costs and model in costs[provider]:
        return costs[provider][model]

    for models in costs.values():
        if model in models:
            return models[model]

    return {"input": 0.001, "output": 0.002}


def _harmonic_mean(
    a: float,
    b: float) -> float:
    if a + b == 0:
        return 0
    return 2 * a * b / (a + b)


class CacheEvaluator:
    """
    Evaluate semantic cache effectiveness with precision, recall, and F1 metrics.

    Usage:
        evaluator = CacheEvaluator(true_labels, cache_results)
        metrics = evaluator.get_metrics(distance_threshold=0.3)
        print(f"Precision: {metrics['precision']:.2%}")
        print(f"Recall: {metrics['recall']:.2%}")
        print(f"F1 Score: {metrics['f1_score']:.2%}")
    """

    def __init__(
        self,
        true_labels: list[bool],
        cache_results: list[CacheResults],
        is_from_full_retrieval: bool = False,
    ) -> None:
        self.true_labels = np.array(true_labels)
        self.cache_results = np.array(cache_results)
        self.is_from_full_retrieval = is_from_full_retrieval

    @classmethod
    def from_full_retrieval(
        cls,
        true_labels: list[bool],
        cache_results: list[CacheResults]) -> "CacheEvaluator":
        """Create evaluator from full retrieval results.

        Returns:
            A CacheEvaluator configured for full-retrieval evaluation.
        """
        return cls(true_labels, cache_results, is_from_full_retrieval=True)

    def matches_df(self) -> pd.DataFrame:
        """Get DataFrame of query-match-distance-label tuples.

        Returns:
            DataFrame with query, match, distance, and true_label columns.
        """
        query = [r.query for r in self.cache_results]
        match = [r.matches[0].prompt if len(r.matches) > 0 else None for r in self.cache_results]
        distance = [
            r.matches[0].vector_distance if len(r.matches) > 0 else None for r in self.cache_results
        ]
        true_label = self.true_labels.tolist()

        return pd.DataFrame(
            {
                "query": query,
                "match": match,
                "distance": distance,
                "true_label": true_label,
            }
        )

    def get_metrics(self, distance_threshold: float | None = None) -> dict[str, Any]:
        """
        Calculate evaluation metrics at given threshold.

        Returns:
            Dict with cache_hit_rate, precision, recall, f1_score, accuracy,
            utility, and confusion_matrix keys.
        """
        T = 1 if distance_threshold is None else distance_threshold

        has_retrieval = np.array(
            [len([m for m in it.matches if m.vector_distance < T]) > 0 for it in self.cache_results]
        )
        true_labels = np.array(self.true_labels)

        if self.is_from_full_retrieval:
            true_labels[~has_retrieval] = ~true_labels[~has_retrieval]

        tp = has_retrieval & true_labels
        tn = (~has_retrieval) & true_labels
        fp = has_retrieval & (~true_labels)
        fn = (~has_retrieval) & (~true_labels)

        TP = sum(tp)
        FP = sum(fp)
        FN = sum(fn)
        TN = sum(tn)

        confusion_matrix = np.array([[TN, FP], [FN, TP]])
        cache_hit_rate = (TP + FP) / (TP + FP + FN + TN) if (TP + FP + FN + TN) > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 1
        recall = TP / (TP + FN) if (TP + FN) > 0 else 1

        return {
            "cache_hit_rate": cache_hit_rate,
            "precision": precision,
            "recall": recall,
            "f1_score": 2 * TP / (2 * TP + FP + FN) if (2 * TP + FP + FN) > 0 else 0,
            "accuracy": (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0,
            "utility": _harmonic_mean(precision, cache_hit_rate),
            "confusion_matrix": confusion_matrix,
        }

    def sweep_thresholds(
        self,
        metric_to_maximize: str = "f1_score",
        threshold_range: tuple = (0, 1),
        num_samples: int = 100,
    ) -> dict[str, Any]:
        """
        Sweep thresholds to find optimal value.

        Returns:
            Dict with best_threshold, all_metrics, and thresholds keys.
        """
        thresholds = np.linspace(threshold_range[0], threshold_range[1], num_samples)
        all_metrics: dict[str, list[Any]] = {}

        for threshold in thresholds:
            metrics = self.get_metrics(float(threshold))
            for key, value in metrics.items():
                if key != "confusion_matrix":
                    if key not in all_metrics:
                        all_metrics[key] = []
                    all_metrics[key].append(value)

        all_metrics_arr = {k: np.array(v) for k, v in all_metrics.items()}
        best_idx = int(np.argmax(all_metrics_arr[metric_to_maximize]))
        best_threshold = float(thresholds[best_idx])

        return {
            "best_threshold": best_threshold,
            "all_metrics": all_metrics_arr,
            "thresholds": thresholds,
        }


class PerfEval:
    """
    Track performance metrics: latency, throughput, and LLM costs.

    Usage:
        perf = PerfEval()
        perf.set_total_queries(len(queries))

        with perf:
            for query in queries:
                perf.start()
                result = cache.check(query)
                if result.matches:
                    perf.tick("cache_hit")
                else:
                    perf.tick("cache_miss")
                    response = llm(query)
                    perf.tick("llm_call")
                    perf.record_llm_call("gpt-4o-mini", query, response)

        metrics = perf.get_metrics(labels=["cache_hit", "llm_call"])
        costs = perf.get_costs()
    """

    def __init__(self) -> None:
        self.durations: list[float] = []
        self.durations_by_label: dict[str, list[float]] = {}
        self.last_time: float | None = None
        self.total_queries: int | None = None
        self.llm_calls: list[dict] = []

    def start(self) -> None:
        """Start timing."""
        self.last_time = time.time()

    def tick(self, label: str | None = None) -> None:
        """Record elapsed time since last start/tick."""
        now = time.time()
        if self.last_time is None:
            self.last_time = now
        dt = now - self.last_time
        self.durations.append(dt)
        if label:
            self.durations_by_label.setdefault(label, []).append(dt)
        self.last_time = now

    def set_total_queries(self, n: int) -> None:
        """Set total number of queries for rate calculations."""
        self.total_queries = n

    def record_llm_call(
        self, model: str, input_text: str, output_text: str, provider: str = "openai"
    ) -> None:
        """
        Record an LLM call for cost tracking.

        Args:
            model: Model name (e.g., "gpt-4o-mini")
            input_text: Input text
            output_text: Output text
            provider: Provider name (default: "openai")
        """
        input_tokens = count_tokens(input_text, model)
        output_tokens = count_tokens(output_text, model)

        self.llm_calls.append(
            {
                "model": model,
                "provider": provider,
                "in": input_tokens,
                "out": output_tokens,
            }
        )

    def _stats(self, values: list[float]) -> dict[str, float]:
        """Calculate statistics for a list of duration values.

        Returns:
            Dict with count, average_latency_ms, and p50/p90/p95/p99 latency stats.
        """
        if len(values) == 0:
            return {
                "count": 0,
                "average_latency_ms": 0.0,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            }
        arr = np.array(values, dtype=float)
        return {
            "count": int(arr.size),
            "average_latency_ms": float(arr.mean() * 1000.0),
            "p50_ms": float(np.percentile(arr, 50) * 1000.0),
            "p90_ms": float(np.percentile(arr, 90) * 1000.0),
            "p95_ms": float(np.percentile(arr, 95) * 1000.0),
            "p99_ms": float(np.percentile(arr, 99) * 1000.0),
        }

    def get_metrics(self, labels: list[str] | None = None) -> dict[str, Any]:
        """
        Get performance metrics.

        Args:
            labels: List of timing labels to include

        Returns:
            Dict with "overall" and "by_label" metrics
        """
        overall = self._stats(self.durations)
        by_label = {}
        if labels:
            for lbl in labels:
                by_label[lbl] = self._stats(self.durations_by_label.get(lbl, []))
        return {"overall": overall, "by_label": by_label}

    def get_costs(self) -> dict[str, Any]:
        """
        Calculate costs for all recorded LLM calls.

        Returns:
            Dict with total_cost, by_model breakdown, and per-query averages
        """
        total = 0.0
        by_model: dict[str, float] = {}

        for call in self.llm_calls:
            model = call["model"]
            provider = call.get("provider", "openai")
            rates = get_model_cost(provider, model)

            input_cost = (call["in"] / 1000.0) * rates.get("input", 0.0)
            output_cost = (call["out"] / 1000.0) * rates.get("output", 0.0)
            call_cost = input_cost + output_cost

            by_model[model] = by_model.get(model, 0.0) + call_cost
            total += call_cost

        result = {
            "total_cost": total,
            "by_model": by_model,
            "calls": len(self.llm_calls),
        }

        if self.total_queries:
            result["avg_cost_per_query"] = total / self.total_queries
        if self.llm_calls:
            result["avg_cost_per_call"] = total / len(self.llm_calls)

        return result

    def summary(self, labels: list[str] | None = None) -> str:
        """Get a formatted summary of performance metrics.

        Returns:
            Multi-line string summarizing latency and cost metrics.
        """
        metrics = self.get_metrics(labels)
        costs = self.get_costs()

        lines = ["Performance Summary", "=" * 40]

        if self.total_queries:
            lines.append(f"Total Queries: {self.total_queries}")

        overall = metrics["overall"]
        lines.extend((f"Average Latency: {overall['average_latency_ms']:.1f}ms", f"P50 Latency: {overall['p50_ms']:.1f}ms", f"P95 Latency: {overall['p95_ms']:.1f}ms"))

        if labels:
            lines.extend(("", "By Label:"))
            for label in labels:
                if label in metrics["by_label"]:
                    stats = metrics["by_label"][label]
                    lines.append(
                        f"  {label}: {stats['count']} calls, {stats['average_latency_ms']:.1f}ms avg"
                    )

        if costs["calls"] > 0:
            lines.extend(("", f"LLM Calls: {costs['calls']}", f"Total Cost: ${costs['total_cost']:.4f}"))
            if "avg_cost_per_query" in costs:
                lines.append(f"Avg Cost/Query: ${costs['avg_cost_per_query']:.6f}")

        return "\n".join(lines)
