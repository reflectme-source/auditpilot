# Source-rights evidence v1

`source-rights-evidence/1` is a provider-neutral structured evidence artifact for recording what a producer reports it observed about machine-readable source-side rights declarations at a specific time.

It is deliberately separate from AuditPilot's document upload pipeline and from compliance scoring.

## Trust boundary

The artifact separates three independent dimensions:

1. **Declaration state** — what the producing workflow reports it observed for the supplied source and intended purpose.
2. **Integrity state** — what the producer reports about signature verification of the raw artifact.
3. **Freshness** — whether the observation is current relative to a reviewer-controlled evaluation clock.

An imported `integrity.verification_status: "verified"` is **producer-reported metadata**. AuditPilot validating this JSON against the schema does not verify a cryptographic signature and must not present the field as an AuditPilot verification result.

The normalized artifact should retain a complete digest/reference to the raw signed artifact so a separate trusted verifier can tie the record back to exactly what was checked.

## Policy boundary

This evidence class does not establish:

- permission;
- ownership;
- licence validity;
- lawful access;
- legal clearance;
- framework compliance.

`interpretation.legal_clearance` is therefore fixed to `false`.

A current, producer-reported verified observation of a prohibition or licence requirement is still valid evidence of that declaration. It is not permission. Likewise, `unknown`, `no_machine_readable_declaration_observed`, stale, conflicting, failed-verification, and untrusted-key states remain unresolved review inputs.

No state in this schema automatically marks an AuditPilot control compliant.

## Review behavior

A deterministic consumer can classify freshness using a fixed evaluation clock:

- `observed_at` after the evaluation clock: invalid/future observation;
- `expires_at` before `observed_at`: invalid interval;
- `expires_at` at or before the evaluation clock: stale;
- otherwise: current.

Recommended review routing:

| Declaration / integrity / freshness | Review behavior |
|---|---|
| explicit declaration + producer-reported verified + current | usable as one evidence item; still no automatic compliance conclusion |
| stale | human review |
| `unknown` or no declaration observed | human review; never permission |
| `conflict` | human review |
| `failed` or `untrusted_key` | untrusted evidence / human review |
| future observation or invalid interval | invalid evidence |

## Schema and fixtures

- Schema: `schemas/source-rights-evidence-v1.schema.json`
- Synthetic fixtures: `examples/source-rights-evidence/`
- Deterministic validation/freshness tests: `backend/tests/test_source_rights_evidence.py`

All examples use synthetic domains, identifiers, fingerprints, and complete synthetic SHA-256 values. They do not describe the current rights state of any real resource.

## Integration boundary

This first contribution intentionally contains no:

- provider API client;
- MCP integration;
- payment logic;
- URL dereferencing;
- signature implementation;
- importer endpoint;
- compliance-score changes.

A live provider adapter, if ever needed, belongs outside this schema and should normalize only after provider-specific verification has completed.
