# Development Guide

## Development principles

Development must be slow, explicit and verifiable.

The project should prioritize architectural correctness over immediate functionality.

Every layer should be understandable before another layer is added.

## Core workflow

For any capability that performs real actions, follow this pattern:

```text
Observe
  ↓
Plan
  ↓
Execute
  ↓
Verify
  ↓
Respond
```

The assistant must not claim that an operation happened unless the operation was executed by a tool and verified.

## Current architecture

Current execution flow:

```text
local-assistant
  ↓
CLI
  ↓
Orchestrator
  ↓
VaultAgent
  ↓
Vault tools
  ↓
Markdown files
```

Current Vault tools:

- `read_note`
- `search_notes`
- `append_note`
- `write_note`
- `list_folders`
- `create_folder`
- `delete_folder`

## Local setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

Editable mode allows the `local-assistant` command to use the current repository code directly.

## Running the CLI

Show help:

```bash
local-assistant --help
```

Use the sample Vault:

```bash
local-assistant \
  --vault-path examples/sample_vault \
  search-notes Vault
```

### Folder commands

List folders in the Vault root:

```bash
local-assistant --vault-path examples/sample_vault list-folders
```

List folders inside a nested folder:

```bash
local-assistant --vault-path examples/sample_vault list-folders projects
```

Create a folder:

```bash
local-assistant --vault-path examples/sample_vault create-folder projects
```

Create a nested folder:

```bash
local-assistant --vault-path examples/sample_vault create-folder projects/salesforce
```

Delete an empty folder:

```bash
local-assistant --vault-path examples/sample_vault delete-folder projects/archive
```

Folder deletion is intentionally conservative. It only deletes empty folders and refuses to delete files, symlinks, non-empty folders, the Vault root, or paths outside the Vault.

### Real Vault

Use a real Vault:

```bash
LOCAL_ASSISTANT_VAULT_PATH=/path/to/your/vault \
local-assistant search-notes "Salesforce"
```

## Running tests

Run the full test suite:

```bash
python -m pytest
```

Run a specific test file:

```bash
python -m pytest tests/unit/test_cli.py
```

Run a specific test:

```bash
python -m pytest tests/unit/test_cli.py::test_cli_read_note
```

## Branching

Use `main` for stable code.

Use `develop` for active development.

Feature work should happen on dedicated branches from `develop`.

Suggested flow:

```bash
git switch develop
git switch -c feature/my-change
```

Merge feature branches back into `develop` only after tests pass.

Merge `develop` into `main` only when the milestone is stable.

## Commit style

Prefer small commits.

Each commit should represent one meaningful change.

Examples:

```text
Add baseline architecture documentation
Add Ollama provider interface
Add read note tool
Add structured CLI
Add installable CLI entry point
```

Avoid commits that mix unrelated work.

## Documentation discipline

Documentation is first-class.

Whenever a major design decision is made, update or create an ADR.

Whenever a new agent is introduced, document:

- responsibility;
- boundaries;
- tools it may use;
- tools it may not use;
- failure behavior.

Whenever a new tool is introduced, document:

- purpose;
- input;
- output;
- side effects;
- verification strategy;
- failure cases.

## Configuration

No personal paths should be hardcoded.

Invalid example:

```text
/home/user/Documents/Vault
```

Valid approach:

```text
Read the Vault path from configuration.
```

Configuration containing personal paths should not be committed.

Example configuration files may be committed only if they contain safe placeholder values.

## Runtime data

Runtime data belongs under `var/`.

The contents of `var/` are not committed.

Typical runtime data:

- logs;
- temporary state;
- cache;
- local databases.

## Personal data

Personal data must stay outside the repository.

Do not commit:

- real Vault contents;
- private notes;
- PDFs;
- images;
- books;
- emails;
- transcripts;
- embeddings generated from personal content;
- indexes generated from personal content;
- local model files.

## Testing strategy

Tests should exist for each real operation.

Minimum expected tests for tools:

- success case;
- missing input;
- invalid path;
- permission or write failure where applicable;
- verification failure where applicable.

The integration surface currently covered by tests includes:

- Vault tools;
- VaultAgent;
- Orchestrator;
- structured CLI.

## Prompt development

Prompts are part of system behavior and are versioned under `prompts/`.

Prompts should be treated like source code:

- readable;
- scoped;
- reviewed;
- committed;
- changed intentionally.

Avoid hiding important behavior in untracked local prompts.

## Experiments

Experiments belong under `experiments/`.

Experimental code must not leak into production code unless deliberately promoted.

Rejected experiments should be documented when useful.

## Dependency policy

Do not add libraries before they are needed.

Avoid introducing large frameworks during the first milestone.

Every dependency should have a clear architectural role.

When adding a dependency, document:

- why it is needed;
- where it fits;
- whether it is replaceable;
- what it replaces or simplifies.

## Current development constraint

The system now has a working structured CLI.

The next step may introduce LLM-assisted parsing, but it must remain controlled.

The LLM should not execute tools directly.

A safe future flow is:

```text
Natural language request
  ↓
LLM proposes structured command
  ↓
System validates command
  ↓
Human reviews or command is safely executable
  ↓
Orchestrator executes
  ↓
Tool verifies result
```

Until this is implemented, avoid:

- free-form autonomous agents;
- background execution;
- unreviewed write operations;
- advanced RAG;
- vector databases;
- multimodal processing;
- orchestration frameworks;
- multi-agent collaboration.


## LLM-assisted proposal flow

The current controlled natural-language flow is:

```text
Natural language request
  ↓
LLM
  ↓
CommandProposal
  ↓
local validation
  ↓
printed proposal
```

Execution is separate:

```text
CommandProposal JSON
  ↓
ExecuteCommandProposal
  ↓
validation
  ↓
confirmation gate for writes
  ↓
Orchestrator
  ↓
VaultAgent
  ↓
Vault tools
```

The LLM must not execute tools directly.

The LLM must not bypass validation.

The LLM must not decide whether a write operation can skip confirmation.

Write operations always require explicit confirmation at execution time.

### Example

```bash
local-assistant --json propose "cerca Salesforce nel vault" > /tmp/proposal.json

local-assistant execute-proposal /tmp/proposal.json
```

For writes:

```bash
local-assistant --json propose \
  "crea la nota idee/test.md con contenuto # Test" \
  > /tmp/proposal-write.json

local-assistant execute-proposal /tmp/proposal-write.json --confirm
```

### Development rule

Any future natural-language feature must preserve this boundary:

```text
LLM proposes.
System validates.
Human confirms side effects.
Tools execute.
Tools verify.
```


## Controlled ask command

The controlled `ask` command is the first convenient natural-language interface.

Flow:

```text
User request
  ↓
ControlledAsk
  ↓
CommandProposer
  ↓
CommandProposalValidator
  ↓
ExecuteCommandProposal
  ↓
Orchestrator
  ↓
VaultAgent
  ↓
Vault tools
```

The command may execute read-only operations immediately.

Current read-only operations:

- `read_note`
- `search_notes`
- `list_folders`

The command must not execute write operations unless `--confirm` is passed.

Current write operations:

- `append_note`
- `write_note`
- `create_folder`
- `delete_folder`

Example:

```bash
local-assistant ask "cerca Salesforce"
```

Write example:

```bash
local-assistant ask "crea la nota idee/test.md con contenuto # Test"
```

This must fail with:

```text
CONFIRMATION_REQUIRED
```

Confirmed write:

```bash
local-assistant ask "crea la nota idee/test.md con contenuto # Test" --confirm
```

### Development rule

Do not add autonomous loops on top of `ask`.

`ask` is a one-step controlled command:

```text
one user request
  ↓
one proposal
  ↓
one validation
  ↓
zero or one execution
```

Any future multi-step behavior must be introduced as a separate architectural decision.
