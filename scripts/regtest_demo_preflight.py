#!/usr/bin/env python3
"""Decision-gated regtest preflight for Axven Bitcoin PQ Lab.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This helper binds a real regtest UTXO observation to a machine-readable lab
report without selecting a PQ scheme, hybrid authorization semantics, Bitcoin
consensus changes, activation, legacy/lost UTXO treatment, recovery authority,
trust roots, or key custody.
"""

from __future__ import annotations

import argparse
import json
import re

_TXID_RE = re.compile(r"^[0-9a-f]{64}$")


def build_report(txid: str, vout: int, confirmations: int, amount_btc: str) -> dict:
    if not isinstance(txid, str) or _TXID_RE.fullmatch(txid) is None:
        raise ValueError("txid must be 64 lowercase hexadecimal characters")
    if isinstance(vout, bool) or not isinstance(vout, int) or vout < 0:
        raise ValueError("vout must be a non-negative integer")
    if isinstance(confirmations, bool) or not isinstance(confirmations, int) or confirmations < 1:
        raise ValueError("confirmations must be a positive integer")
    if not isinstance(amount_btc, str) or not amount_btc:
        raise ValueError("amount_btc must be a non-empty decimal string")

    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network": "regtest",
        "experiment": "decision-gated-preflight",
        "bitcoin_core_modified": False,
        "creates_coin_token_or_network": False,
        "scheme_selected": False,
        "hybrid_semantics_selected": False,
        "consensus_change_selected": False,
        "activation_selected": False,
        "legacy_utxo_treatment_selected": False,
        "lost_coin_treatment_selected": False,
        "recovery_authority_selected": False,
        "trust_root_selected": False,
        "key_custody_selected": False,
        "observed_utxo": {
            "txid": txid,
            "vout": vout,
            "confirmations": confirmations,
            "amount_btc": amount_btc,
        },
        "experiment_on_status": "blocked_pending_explicit_security_decisions",
        "required_decisions": [
            "post_quantum_scheme",
            "hybrid_authorization_semantics",
        ],
        "note": (
            "A real Bitcoin Core regtest UTXO was observed. No authorization or "
            "consensus behavior was changed; experiment-on remains fail-closed."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--txid", required=True)
    parser.add_argument("--vout", required=True, type=int)
    parser.add_argument("--confirmations", required=True, type=int)
    parser.add_argument("--amount-btc", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            build_report(args.txid, args.vout, args.confirmations, args.amount_btc),
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
