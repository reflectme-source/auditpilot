# Provider-neutral source-rights evidence

`source-rights-evidence/1` is a small structured evidence artifact for recording what machine-readable source-rights declaration a producer reports observing for a public resource and an explicit intended use.

It is intentionally separate from AuditPilot's document-upload pipeline and compliance scoring. This first contribution contains only a JSON Schema, synthetic fixtures and deterministic validation tests. It performs no network access, URL dereferencing, provider call, signature verification, payment, or policy decision.

## Trust boundary

Three states remain independent:

1. **Declaration state** — what the producer reports was observed, such as a prohibition, licence requirement, conflict or unknown state.
2. **Integrity state** — the producer-reported result of verifying the raw evidence, carried in `integrity.verification_status`.
3. **Freshness** — a consumer-computed result based on `observed_at`, optional `expires_at`, and an explicit evaluation clock.

An imported `verification_status: verified` means **the producer reports that verification succeeded**. AuditPilot validating the JSON Schema does not establish signature authenticity.

Consumers that need cryptographic assurance must verify the original signed artifact outside this schema boundary and apply their own local trust policy. Unknown or untrusted keys must not be silently promoted to trusted evidence.

## Review behavior

All fixtures keep:

- `interpretation.legal_clearance = false`;
- `interpretation.requires_human_review = true`.

A valid and current artifact can be used as one evidence item, but it does not by itself mark a control or organization compliant.

The following remain review conditions rather than permission:

- stale evidence;
- `unknown`;
- no machine-readable declaration observed;
- conflicting declarations;
- failed verification;
- an untrusted signing key;
- freshness that cannot be established.

A current, producer-reported verified observation of a prohibition or licence requirement is still evidence of that declaration. It is not permission.

## Freshness rules used by the tests

The tests use a fixed evaluation clock rather than wall-clock time:

`2026-10-06T12:00:00Z`

The deterministic freshness helper reports:

- `future_observation` when `observed_at` is after the evaluation clock;
- `invalid_range` when `expires_at` is before `observed_at`;
- `unknown` when no `expires_at` is supplied;
- `stale` when `expires_at` is at or before the evaluation clock;
- `current` otherwise.

Freshness is therefore not inferred from declaration or integrity status.

## Synthetic fixtures

The fixtures under `examples/source-rights-evidence/` are fictional and use complete synthetic SHA-256 values. They cover:

- current evidence;
- stale evidence;
- unknown declaration state;
- conflicting declaration state;
- failed producer-reported verification;
- untrusted producer-reported verification key.

The tests additionally reject malformed hashes and timestamps without a timezone, and exercise future observations plus expiry-before-observation ranges.

## Provider neutrality

Provider-specific operation IDs, payment receipts, transport headers, delivery proofs and policy decisions do not belong in this object.

A future importer can accept this normalized artifact without requiring AuditPilot to depend on a particular evidence provider. Any live provider adapter should remain a separate concern and should only be added for a concrete workflow.
