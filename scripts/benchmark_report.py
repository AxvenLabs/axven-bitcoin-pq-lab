#!/usr/bin/env python3
"""Generic benchmark report contract for Axven Bitcoin PQ Lab.

Research only. This helper does not select a PQ scheme, define Bitcoin consensus,
activation, recovery, key custody, trust roots, or mainnet behavior.
"""

from __future__ import annotations

import math
import statistics


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return value


def summarize_samples(samples: list[float | int]) -> dict[str, float]:
    if not isinstance(samples, list) or len(samples) < 3:
        raise ValueError("at least three measured samples are required")
    clean = [_number(value, "sample") for value in samples]
    ordered = sorted(clean)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    return {
        "median": float(statistics.median(ordered)),
        "p95": float(ordered[rank - 1]),
    }


def validate_report(report: dict) -> dict:
    if not isinstance(report, dict):
        raise ValueError("report must be an object")
    if report.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if report.get("research_only") is not True:
        raise ValueError("research_only must be true")

    for key in ("benchmark_name", "category", "source_identity", "timestamp_utc", "unit"):
        value = report.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")

    env = report.get("environment")
    if not isinstance(env, dict):
        raise ValueError("environment must be an object")
    for key in ("os", "architecture", "cpu_model", "runtime"):
        value = env.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"environment.{key} must be a non-empty string")
    for key in ("logical_cpus", "ram_bytes"):
        value = env.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"environment.{key} must be a positive integer")

    warmups = report.get("warmups")
    repetitions = report.get("repetitions")
    if not isinstance(warmups, int) or isinstance(warmups, bool) or warmups < 0:
        raise ValueError("warmups must be a non-negative integer")
    if not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions < 3:
        raise ValueError("repetitions must be an integer >= 3")

    samples = report.get("samples")
    if not isinstance(samples, list) or len(samples) != repetitions:
        raise ValueError("sample count must equal repetitions")
    expected = summarize_samples(samples)

    for key in ("median", "p95"):
        actual = _number(report.get(key), key)
        if actual != expected[key]:
            raise ValueError(f"{key} does not match raw samples")

    return report
