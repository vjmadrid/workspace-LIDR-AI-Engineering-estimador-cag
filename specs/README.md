# Spec Driven Development

This folder is the source of truth for the estimation workflow contracts.

## Workflow

1. Update or add a scenario in `specs/scenarios/`.
2. Update the contract in `specs/contracts/` if the input or output shape changes.
3. Add or adjust a test in `tests/specs/`.
4. Implement the code change in `app/`.
5. Run the spec tests before merging.

## Current scope

- `estimate_request.schema.json`: request contract for the transcription input.
- `estimate_response.schema.json`: response contract for the generated estimation.
- `estimate_success.json`: happy-path scenario.
- `estimate_empty_input.json`: validation scenario for blank input.
