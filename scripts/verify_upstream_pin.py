"""Verify the research-only Bitcoin Core source pin against git metadata.

This script does not patch Bitcoin Core or define consensus behavior. It only proves
that the configured upstream tag resolves to the exact commit recorded by the lab.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PIN = ROOT / "upstream" / "bitcoin-core.json"
EXPECTED_REPOSITORY = "https://github.com/bitcoin/bitcoin.git"
REQUIRED_FIELDS = {"repository", "tag", "tag_object_sha", "commit_sha", "purpose"}
TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


def load_pin(path: pathlib.Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("pin must be a JSON object")

    keys = set(data)
    missing = REQUIRED_FIELDS - keys
    extra = keys - REQUIRED_FIELDS
    if missing:
        raise ValueError(f"pin is missing fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"pin has unexpected fields: {sorted(extra)}")

    for key in REQUIRED_FIELDS:
        if not isinstance(data[key], str):
            raise ValueError(f"{key} must be a string")

    if data["repository"] != EXPECTED_REPOSITORY:
        raise ValueError(
            f"repository must be the canonical Bitcoin Core upstream: {EXPECTED_REPOSITORY}"
        )

    tag = data["tag"]
    if not TAG_RE.fullmatch(tag) or ".." in tag or tag.endswith("."):
        raise ValueError("tag contains unsafe or unsupported characters")

    for key in ("tag_object_sha", "commit_sha"):
        value = data[key]
        if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError(f"{key} must be a lowercase 40-character git object id")

    purpose = data["purpose"].lower()
    if "research" not in purpose or "regtest" not in purpose:
        raise ValueError("purpose must explicitly identify research and regtest use")

    return data


def run(*args: str, cwd: pathlib.Path) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def verify(pin: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory(prefix="axven-btc-pin-") as tmp:
        work = pathlib.Path(tmp)
        run("git", "init", "--quiet", cwd=work)
        run("git", "remote", "add", "origin", pin["repository"], cwd=work)
        run(
            "git",
            "fetch",
            "--quiet",
            "--depth=1",
            "origin",
            f"refs/tags/{pin['tag']}:refs/tags/{pin['tag']}",
            cwd=work,
        )
        tag_object = run("git", "rev-parse", pin["tag"], cwd=work)
        commit = run("git", "rev-parse", f"{pin['tag']}^{{commit}}", cwd=work)
        if tag_object != pin["tag_object_sha"]:
            raise RuntimeError(
                f"tag object mismatch: expected {pin['tag_object_sha']}, got {tag_object}"
            )
        if commit != pin["commit_sha"]:
            raise RuntimeError(
                f"commit mismatch: expected {pin['commit_sha']}, got {commit}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pin", type=pathlib.Path, default=DEFAULT_PIN)
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="validate the local pin file without contacting the upstream repository",
    )
    args = parser.parse_args()

    pin = load_pin(args.pin)
    if not args.metadata_only:
        verify(pin)
    print(
        json.dumps(
            {
                "ok": True,
                "tag": pin["tag"],
                "tag_object_sha": pin["tag_object_sha"],
                "commit_sha": pin["commit_sha"],
                "network_verified": not args.metadata_only,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
