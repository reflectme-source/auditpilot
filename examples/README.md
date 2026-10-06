# Synthetic AuditPilot samples

These are fictional examples. They contain no actual company evidence.

| File | What it demonstrates |
|---|---|
| `messy-risk-register.csv` | Three risks; six findings: two duplicate-ID findings, a missing owner, a missing treatment, an overdue review, and invalid likelihood `9` |
| `corrected-risk-register.csv` | Same risks with those defects corrected; zero findings at generation time |
| `draft-policy.txt` | Draft text requiring human review; still matches A.5.1 keywords |
| `approved-policy.txt` | Approval / version markers and A.5.1 keyword mapping; does not prove real approval |

## Provider-neutral source-rights evidence

`source-rights-evidence/` contains fictional JSON fixtures for the `source-rights-evidence/1` schema. They cover current, stale, unknown, conflicting, failed-verification, and untrusted-key states. The schema and review boundary are documented in [`docs/source-rights-evidence.md`](../docs/source-rights-evidence.md).

These fixtures are evidence-model examples only. They do not grant permission, establish legal clearance, or mark any control compliant.

Use the browser demo at `/demo` to download date-relative CSVs. Checked-in CSVs are snapshots and their future review dates eventually become overdue. Regenerate them with `python scripts/write_samples.py` from the repository root.

Run the complete scenario from `backend` with `uv run python ../scripts/demo.py`.
The register score is a simple heuristic. Control coverage is limited to A.5.1 / A.5.2.
