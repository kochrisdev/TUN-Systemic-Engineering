"""Run an entirely synthetic publication and lost-response demonstration."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .runtime import Host, Principal, Provider


def run(directory):
    provider = Provider(directory / "provider.sqlite3")
    host_path = directory / "host.sqlite3"
    host = Host(host_path, provider)
    alice = Principal("alice-fixture", "sandbox")
    host.set_permission(alice, "project-board", True)
    host.set_dispatch_budget(alice, 3)
    proposal = host.propose(alice, "project-board", "Synthetic project update: the pilot is ready for review.")
    ref = {"id": proposal["id"], "version": proposal["version"]}
    decision = host.decide(alice, ref, "approve", "fixture-approval-1")
    operation = host.reserve(alice, ref, decision["id"])
    unknown = host.dispatch(alice, operation, fault="lost-response")
    # Reopen both stores; no in-memory host state is needed to recover.
    reopened_provider = Provider(directory / "provider.sqlite3")
    restarted = Host(host_path, reopened_provider)
    before_readback = restarted.receipt(alice, operation)
    verified = restarted.reconcile(alice, operation)
    restarted.dispatch(alice, operation)  # Redelivery is a read, not another invocation.
    if (unknown["effectKnowledge"] != "unknown" or before_readback["status"] != "pending-verification"
            or verified["status"] != "completed" or reopened_provider.count() != 1):
        raise RuntimeError("pilot acceptance observation failed")
    return {
        "scenario": "fixture approval -> publication -> lost response -> reopen -> readback",
        "beforeReadback": before_readback,
        "afterReadback": verified,
        "providerPublicationCount": reopened_provider.count(),
        "limits": "Synthetic identities, local stores, no model, no remote publishing, no full conformance claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, help="Create a NEW directory to retain the two synthetic databases")
    args = parser.parse_args()
    if args.directory:
        args.directory.mkdir(parents=True, exist_ok=False)
        result = run(args.directory)
    else:
        with tempfile.TemporaryDirectory(prefix="tse-publication-") as path:
            result = run(Path(path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
