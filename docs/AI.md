# Optional AI-assisted analysis

AuditPilot's AI-assisted review is optional and disabled by default.

The default test and CI workflows do not require an API key and do not make
paid provider calls. Tests use the deterministic fake provider.

## Configuration

AI settings are read from environment variables:

- `AUDITPILOT_AI_ENABLED`
- `AUDITPILOT_AI_PROVIDER`
- `AUDITPILOT_AI_MODEL`
- `AUDITPILOT_AI_API_KEY`
- `AUDITPILOT_AI_TIMEOUT_SECONDS`
- `AUDITPILOT_AI_MAX_INPUT_CHARS`
- `AUDITPILOT_AI_MAX_OUTPUT_TOKENS`
- `AUDITPILOT_AI_MAX_RETRIES`

AI remains disabled unless `AUDITPILOT_AI_ENABLED` is explicitly enabled.

External providers also require explicit approval on each analysis request
before document text may be sent outside the running AuditPilot instance.

## Optional OpenAI smoke test

A real-provider smoke test is optional and must not run in default CI.

Set the required configuration locally:

```bash
export AUDITPILOT_AI_ENABLED=true
export AUDITPILOT_AI_PROVIDER=openai
export AUDITPILOT_AI_MODEL="<model-name>"
export AUDITPILOT_AI_API_KEY="<api-key>"