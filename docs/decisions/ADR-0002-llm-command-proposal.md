# ADR-0002: LLM Command Proposal and Controlled Execution

## Status

Accepted.

## Date

2026-06-26

## Context

The project has introduced a local LLM provider and a structured Vault command system.

The assistant can currently:

- receive explicit CLI commands;
- route them through the orchestrator;
- delegate Vault operations to the VaultAgent;
- execute real tools;
- verify write operations.

The next architectural question is how to introduce natural language without allowing the LLM to execute tools directly.

A free-form agent loop would be premature because the project has strict safety and verification requirements:

- the LLM must not perform real actions;
- the LLM must not claim execution;
- write operations must remain controlled;
- tool execution must remain explicit and verifiable;
- the human must retain control over side effects.

## Decision

The LLM is allowed to propose structured commands.

The LLM is not allowed to execute commands.

The flow is:

```text
Natural language request
  ↓
LLM
  ↓
CommandProposal JSON
  ↓
local validation
  ↓
printed proposal
```

Execution is a separate flow:

```text
CommandProposal JSON
  ↓
ExecuteCommandProposal action
  ↓
validation
  ↓
confirmation gate for write operations
  ↓
Orchestrator
  ↓
VaultAgent
  ↓
Vault tools
```

The CLI exposes this as two separate commands:

```bash
local-assistant --json propose "search Salesforce in the vault" > proposal.json

local-assistant execute-proposal proposal.json
```

For write operations:

```bash
local-assistant execute-proposal proposal.json --confirm
```

Write operations must not execute without explicit confirmation.

## Current supported proposal domain

Only the `vault` domain is supported.

Allowed operations:

- `read_note`
- `search_notes`
- `append_note`
- `write_note`

Unsupported domains and unsupported operations are rejected locally.

## Validation rules

A proposal must be rejected if:

- the domain is unsupported;
- the operation is unsupported;
- required arguments are missing;
- unknown arguments are present;
- argument types are invalid;
- required string arguments are empty;
- `relative_path` is absolute;
- `relative_path` contains `..`;
- `overwrite` is present but not boolean.

Write operations always require confirmation, regardless of what the LLM says.

## Consequences

Positive consequences:

- natural language can be introduced without granting autonomy;
- the LLM remains replaceable;
- tool execution remains deterministic and testable;
- write operations remain human-controlled;
- proposal generation can be improved independently from execution;
- invalid or unsafe proposals are rejected before reaching tools.

Negative consequences:

- interaction is less fluid than a full chat agent;
- users must perform multiple steps for natural-language-driven writes;
- some valid user intentions may be rejected if the proposal format is imperfect;
- there is duplicated validation between proposal generation and execution.

## Rationale for duplicated validation

Validation exists in both the proposal layer and execution action.

This is intentional.

The proposal layer validates LLM output before displaying it as trustworthy.

The execution action validates again before performing real operations.

No execution path should rely only on the LLM-facing validation layer.

## Alternatives considered

### Let the LLM call tools directly

Rejected.

This would violate the rule that real operations must be explicit, inspectable and verifiable.

### Add a free-form chat loop immediately

Rejected.

The system is not mature enough for autonomous planning or multi-step agent loops.

### Execute read-only proposals automatically

Deferred.

Read-only operations are lower risk, but automatic execution would still mix proposal and execution too early.

The current design keeps the boundary explicit.

### Use LangGraph immediately

Rejected for this phase.

LangGraph may later orchestrate proposal, validation, confirmation and execution, but the domain contracts must remain independent from a workflow framework.

## Validation

This decision is valid if:

- natural language requests produce structured proposals;
- proposals are validated locally;
- invalid proposals fail safely;
- write proposals do not execute without `--confirm`;
- execution still flows through the orchestrator and tools;
- tests cover proposal validation and controlled execution.
