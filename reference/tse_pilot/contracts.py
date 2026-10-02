"""Experimental pilot contracts; schemas do not authenticate records."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "tse-pilot/0.3"
MAX_BYTES = 65536
SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"
SCHEMAS = {f"tse-pilot/{version}": json.loads((SCHEMA_ROOT / f"pilot-v{version}.schema.json").read_text(encoding="utf-8"))
           for version in ("0.1", "0.2", "0.3")}
for _schema in SCHEMAS.values():
    Draft202012Validator.check_schema(_schema)
SCHEMA = SCHEMAS[SCHEMA_VERSION]
VALIDATORS = {version: Draft202012Validator(schema) for version, schema in SCHEMAS.items()}


class ContractError(ValueError):
    """Bounded public error; raw payloads are intentionally excluded."""


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise ContractError("non-JSON numeric constant")


def decode(raw: str) -> dict:
    if not isinstance(raw, str):
        raise ContractError("JSON input must be text")
    try:
        size = len(raw.encode("utf-8"))
    except UnicodeError as exc:
        raise ContractError("invalid JSON encoding") from exc
    if size > MAX_BYTES:
        raise ContractError("record exceeds size limit")
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid JSON record") from exc
    validate(value)
    return value


def canonical(value: dict) -> str:
    # Pilot-specific sorted, ASCII-escaped JSON; NOT RFC 8785/JCS.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def moment(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError("timezone missing")
        return parsed
    except (ValueError, TypeError) as exc:
        raise ContractError("invalid timestamp") from exc


def validate(record: dict, kind: str | None = None) -> None:
    try:
        if len(canonical(record).encode("utf-8")) > MAX_BYTES:
            raise ContractError("record exceeds size limit")
        validator = VALIDATORS.get(record.get("schemaVersion")) if isinstance(record, dict) else None
        if validator is None or next(validator.iter_errors(record), None) is not None:
            raise ContractError("record does not match pilot schema")
        if kind is not None and record["kind"] != kind:
            raise ContractError("unexpected record family")
        for field in ("createdAt", "expiresAt", "observedAt"):
            if field in record:
                moment(record[field])
    except (TypeError, ValueError, RecursionError, UnicodeError) as exc:
        raise ContractError("invalid record value") from exc


def fingerprint(proposal: dict) -> str:
    material = {key: value for key, value in proposal.items() if key != "binding"}
    return "sha256:" + hashlib.sha256(canonical(material).encode("ascii")).hexdigest()


def validate_proposal(proposal: dict) -> None:
    validate(proposal, "ActionProposal")
    if proposal["binding"] != fingerprint(proposal):
        raise ContractError("proposal material binding mismatch")
    if moment(proposal["expiresAt"]) <= moment(proposal["createdAt"]):
        raise ContractError("proposal validity interval is empty")
    if proposal["schemaVersion"] == SCHEMA_VERSION:
        publication = proposal["actionType"] == "publish"
        if publication != (proposal["recoveryFor"] is None and proposal["expectedResourceVersion"] is None):
            raise ContractError("invalid action recovery binding")
        if not publication and (proposal["recoveryFor"] is None or proposal["expectedResourceVersion"] is None):
            raise ContractError("recovery requires a resource revision")


def validate_binding(record: dict, proposal: dict) -> None:
    validate(record)
    validate_proposal(proposal)
    expected = {"id": proposal["id"], "version": proposal["version"]}
    if (record.get("proposalRef") != expected or record.get("binding") != proposal["binding"]
            or record["scope"] != proposal["scope"]):
        raise ContractError("cross-record proposal binding mismatch")
