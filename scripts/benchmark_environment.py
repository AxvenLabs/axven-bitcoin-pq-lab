#!/usr/bin/env python3
"""Collect reproducible benchmark environment metadata for Axven Bitcoin PQ Lab.

Research only. This helper records machine/runtime context for lab measurements.
It does not select a PQ scheme or define Bitcoin consensus, activation, recovery,
trust roots, key custody, or mainnet behavior.
"""

from __future__ import annotations

import json
import os
import platform
import sys


def _cpu_model() -> str:
    candidates = [platform.processor(), platform.machine()]
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as handle:
            for line in handle:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                if key.strip().lower() in {"model name", "hardware", "processor"} and value.strip():
                    candidates.insert(0, value.strip())
                    break
    except OSError:
        pass
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def _ram_bytes() -> int:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        pages = os.sysconf("SC_PHYS_PAGES")
        value = int(page_size) * int(pages)
        if value > 0:
            return value
    except (AttributeError, OSError, ValueError):
        pass
    return 1


def collect_environment() -> dict[str, object]:
    logical_cpus = os.cpu_count() or 1
    return {
        "os": platform.system().lower() or "unknown",
        "architecture": platform.machine() or "unknown",
        "cpu_model": _cpu_model(),
        "logical_cpus": int(logical_cpus),
        "ram_bytes": _ram_bytes(),
        "runtime": f"python-{platform.python_version()}",
    }


def main() -> None:
    json.dump(collect_environment(), sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
