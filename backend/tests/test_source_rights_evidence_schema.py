from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "schemas" / "source-rights-evidence-v1.schema.json"
FIXTURE_DIRECTORY = REPOSITORY_ROOT / "examples" / "source-rights-evidence"
FIXED_CLOCK = datetime.fromisoformat("2026-10-06T12:00:00+00:00")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


SCHEMA = load_json(SCHEMA_PATH)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def validate_artifact(artifact: dict[str, object]) -> None:
    VALIDATOR.validate(artifact)


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def freshness_state(
    artifact: dict[str, object],
    evaluated_at: datetime = FIXED_CLOCK,
) -> str:
    observation = artifact["observation"]
    assert isinstance(observation, dict)

    observed_at_value = observation["observed_at"]
    assert isinstance(observed_at_value, str)
    observed_at = parse_timestamp(observed_at_value)

    if observed_at > evaluated_at:
        return "future_observation"

    expires_at_value = observation["expires_at"]
    if expires_at_value is None:
        return "unknown"

    assert isinstance(expires_at_value, str)
    expires_at = parse_timestamp(expires_at_value)

    if expires_at < observed_at:
        return "invalid_range"
    if expires_at <= evaluated_at:
        return "stale"
    return "current"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "current.json",
        "stale.json",
        "unknown.json",
        "conflict.json",
        "failed.json",
        "untrusted.json",
    ],
)
def test_synthetic_fixtures_match_schema(fixture_name: str) -> None:
    validate_artifact(load_json(FIXTURE_DIRECTORY / fixture_name))


def test_declaration_integrity_and_freshness_are_independent() -> None:
    artifact = load_json(FIXTURE_DIRECTORY / "failed.json")

    assert artifact["observation"]["declaration_state"] == (
        "declared_prohibited_for_purpose"
    )
    assert artifact["integrity"]["verification_status"] == "failed"
    assert freshness_state(artifact) == "current"


def test_current_and_stale_use_fixed_clock() -> None:
    assert freshness_state(load_json(FIXTURE_DIRECTORY / "current.json")) == "current"
    assert freshness_state(load_json(FIXTURE_DIRECTORY / "stale.json")) == "stale"


def test_missing_expiry_keeps_freshness_unknown() -> None:
    artifact = deepcopy(load_json(FIXTURE_DIRECTORY / "current.json"))
    artifact["observation"]["expires_at"] = None

    validate_artifact(artifact)
    assert freshness_state(artifact) == "unknown"


def test_malformed_hash_is_rejected() -> None:
    artifact = deepcopy(load_json(FIXTURE_DIRECTORY / "current.json"))
    artifact["integrity"]["raw_artifact_sha256"] = "sha256:not-a-complete-digest"

    with pytest.raises(ValidationError):
        validate_artifact(artifact)


def test_timestamp_without_timezone_is_rejected() -> None:
    artifact = deepcopy(load_json(FIXTURE_DIRECTORY / "current.json"))
    artifact["observation"]["observed_at"] = "2026-10-06T10:30:00"

    with pytest.raises(ValidationError):
        validate_artifact(artifact)


def test_future_observation_is_not_current() -> None:
    artifact = deepcopy(load_json(FIXTURE_DIRECTORY / "current.json"))
    artifact["observation"]["observed_at"] = "2026-10-06T12:30:00Z"
    artifact["observation"]["expires_at"] = "2026-10-06T13:30:00Z"

    validate_artifact(artifact)
    assert freshness_state(artifact) == "future_observation"


def test_expiry_before_observation_is_invalid_range() -> None:
    artifact = deepcopy(load_json(FIXTURE_DIRECTORY / "current.json"))
    artifact["observation"]["observed_at"] = "2026-10-06T10:30:00Z"
    artifact["observation"]["expires_at"] = "2026-10-06T10:00:00Z"

    validate_artifact(artifact)
    assert freshness_state(artifact) == "invalid_range"


def test_no_fixture_claims_legal_clearance_or_auto_compliance() -> None:
    for fixture_path in FIXTURE_DIRECTORY.glob("*.json"):
        artifact = load_json(fixture_path)

        assert artifact["interpretation"]["legal_clearance"] is False
        assert artifact["interpretation"]["requires_human_review"] is True
