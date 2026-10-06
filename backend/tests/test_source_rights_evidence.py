from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "source-rights-evidence-v1.schema.json"
FIXTURES_DIR = ROOT / "examples" / "source-rights-evidence"
FIXED_NOW = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)

FIXTURE_NAMES = (
    "current-prohibition.json",
    "stale-license-required.json",
    "unknown.json",
    "conflict.json",
    "failed-verification.json",
    "untrusted-key.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def parse_rfc3339(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone required")
    return parsed.astimezone(timezone.utc)


def freshness_state(artifact: dict[str, Any], *, evaluated_at: datetime) -> str:
    observation = artifact["observation"]
    observed_at = parse_rfc3339(observation["observed_at"])
    expires_raw = observation.get("expires_at")
    expires_at = parse_rfc3339(expires_raw) if expires_raw is not None else None

    if observed_at > evaluated_at:
        return "future"
    if expires_at is not None and expires_at < observed_at:
        return "invalid_interval"
    if expires_at is not None and expires_at <= evaluated_at:
        return "stale"
    return "current"


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_synthetic_fixtures_match_schema(
    validator: Draft202012Validator,
    name: str,
) -> None:
    artifact = load_json(FIXTURES_DIR / name)
    validator.validate(artifact)


def test_schema_rejects_malformed_hash(
    validator: Draft202012Validator,
) -> None:
    artifact = load_json(FIXTURES_DIR / "current-prohibition.json")
    artifact["integrity"]["raw_artifact_sha256"] = "sha256:not-a-complete-digest"

    with pytest.raises(ValidationError):
        validator.validate(artifact)


@pytest.mark.parametrize(
    ("field_path", "bad_value"),
    (
        (("observation", "observed_at"), "2026-10-06T11:00:00"),
        (("integrity", "verified_at"), "2026-10-06T11:00:02"),
    ),
)
def test_schema_rejects_timestamps_without_timezone(
    validator: Draft202012Validator,
    field_path: tuple[str, str],
    bad_value: str,
) -> None:
    artifact = load_json(FIXTURES_DIR / "current-prohibition.json")
    artifact[field_path[0]][field_path[1]] = bad_value

    with pytest.raises(ValidationError):
        validator.validate(artifact)


def test_freshness_uses_fixed_clock() -> None:
    current = load_json(FIXTURES_DIR / "current-prohibition.json")
    stale = load_json(FIXTURES_DIR / "stale-license-required.json")

    assert freshness_state(current, evaluated_at=FIXED_NOW) == "current"
    assert freshness_state(stale, evaluated_at=FIXED_NOW) == "stale"


def test_future_observation_is_not_current() -> None:
    artifact = load_json(FIXTURES_DIR / "current-prohibition.json")
    artifact["observation"]["observed_at"] = "2026-10-06T12:00:01Z"
    artifact["observation"]["expires_at"] = "2026-10-06T13:00:00Z"

    assert freshness_state(artifact, evaluated_at=FIXED_NOW) == "future"


def test_expiry_before_observation_is_invalid() -> None:
    artifact = load_json(FIXTURES_DIR / "current-prohibition.json")
    artifact["observation"]["observed_at"] = "2026-10-06T11:00:00Z"
    artifact["observation"]["expires_at"] = "2026-10-06T10:59:59Z"

    assert freshness_state(artifact, evaluated_at=FIXED_NOW) == "invalid_interval"


def test_declaration_integrity_and_freshness_are_independent() -> None:
    artifact = load_json(FIXTURES_DIR / "failed-verification.json")

    assert artifact["observation"]["declaration_state"] == "declared_permitted_for_purpose"
    assert artifact["integrity"]["verification_status"] == "failed"
    assert freshness_state(artifact, evaluated_at=FIXED_NOW) == "current"
    assert artifact["interpretation"]["legal_clearance"] is False
    assert artifact["interpretation"]["requires_human_review"] is True


def test_verified_prohibition_is_evidence_not_permission() -> None:
    artifact = load_json(FIXTURES_DIR / "current-prohibition.json")

    assert artifact["integrity"]["verification_status"] == "verified"
    assert artifact["observation"]["declaration_state"] == "declared_prohibited_for_purpose"
    assert freshness_state(artifact, evaluated_at=FIXED_NOW) == "current"
    assert artifact["interpretation"] == {
        "legal_clearance": False,
        "requires_human_review": True,
    }


def test_schema_cannot_claim_legal_clearance(
    validator: Draft202012Validator,
) -> None:
    artifact = copy.deepcopy(load_json(FIXTURES_DIR / "current-prohibition.json"))
    artifact["interpretation"]["legal_clearance"] = True

    with pytest.raises(ValidationError):
        validator.validate(artifact)
