# ADR-0003: Controlled Ask Command

## Status

Accepted.

## Date

2026-06-26

## Context

The project now supports two separate natural-language-related flows:

```text
propose
  ↓
LLM produces CommandProposal
  ↓
local validation
  ↓
proposal is printed
```

and:

```text
execute-proposal
  ↓
validated CommandProposal JSON
  ↓
confirmation gate for writes
  ↓
Orchestrator
  ↓
VaultAgent
  ↓
Vault tools
```

This separation is safe, but operationally verbose for read-only tasks.

A user should be able to ask simple questions such as:

```bash
local-assistant ask "cerca Salesforce nel vault"
```

without manually saving and executing a proposal JSON file.

The architectural challenge is to make this more convenient without turning the system into an uncontrolled autonomous agent.

## Decision

Introduce a controlled `ask` command.

The command performs:

```text
Natural language request
  ↓
LLM command proposal
  ↓
local validation
  ↓
controlled execution
```

Read-only operations may execute immediately.

Current read-only operations:

- `read_note`
- `search_notes`

Write operations must not execute unless explicitly confirmed.

Current write operations:

- `append_note`
- `write_note`

Write operations require:

```text
--confirm
```

Example:

```bash
local-assistant ask "crea la nota idee/test.md con contenuto # Test"
```

must fail with:

```text
CONFIRMATION_REQUIRED
```

The write may execute only with:

```bash
local-assistant ask "crea la nota idee/test.md con contenuto # Test" --confirm
```

## Resulting modes

The system now supports three interaction modes.

### Explicit structured commands

```bash
local-assistant search-notes "Salesforce"
```

This bypasses the LLM and executes a known command directly.

### Separate proposal and execution

```bash
local-assistant --json propose "cerca Salesforce" > proposal.json

local-assistant execute-proposal proposal.json
```

This is the most inspectable flow.

### Controlled ask

```bash
local-assistant ask "cerca Salesforce"
```

This is the most convenient flow, but still controlled by validation and confirmation rules.

## Safety rule

The LLM never executes tools directly.

The LLM only proposes.

The system validates.

The orchestrator executes.

Tools verify.

## Confirmation rule

Confirmation is determined by local validation rules, not by the LLM.

Even if the LLM returns:

```json
{
  "requires_confirmation": false
}
```

for a write operation, the system must normalize it to:

```json
{
  "requires_confirmation": true
}
```

## Consequences

Positive consequences:

- read-only natural-language operations become convenient;
- write operations remain protected;
- the LLM remains a proposer, not an executor;
- the same validation rules are reused;
- the command is useful without introducing a full agent loop.

Negative consequences:

- the ask command may feel like a chatbot, even though it is not;
- users must understand that write operations need `--confirm`;
- LLM proposal quality still affects usability;
- failed proposals may require falling back to structured commands.

## Alternatives considered

### Keep only propose + execute-proposal

Rejected as the only interface.

It is safe but too verbose for common read-only operations.

### Allow all valid proposals to execute automatically

Rejected.

Write operations must remain explicitly confirmed.

### Add a full autonomous agent loop

Rejected.

The project is not ready for autonomous multi-step execution.

The current system has one-step controlled execution only.

## Validation

This decision is valid if:

- `ask` can execute `read_note` and `search_notes`;
- `ask` refuses `append_note` and `write_note` without `--confirm`;
- `ask --confirm` can execute write operations;
- all execution still flows through the orchestrator;
- all tool write verification remains active;
- tests cover read, search, write-without-confirmation, and write-with-confirmation.
