# Architecture

## Baseline

This document describes the baseline architecture of the Local Assistant project.

The current architecture is intentionally simple.

Complex frameworks, advanced RAG, context compression, multi-agent planning and multimodal processing are explicitly postponed until the first minimal agent works end-to-end.

## System layers

```text
Human
  ↓
Orchestrator
  ↓
Specialized Agents
  ↓
Actions
  ↓
Tools
  ↓
Resources
  ↓
LLM
```

### Human

The human gives goals, constraints and approval.

The system should remain understandable and inspectable by the human.

The assistant should not hide real actions behind vague language.

### Orchestrator

The orchestrator decides:

- which agent should handle a request;
- whether multiple agents are required;
- in which order work should happen;
- how results should be aggregated.

The orchestrator must not know implementation details of tools.
It should not know how to read a file, run a command or search a Git repository.
It delegates domain-specific work to agents.

### Agents

An agent owns one domain.

Examples:

- Vault Agent;
- Linux Agent;
- Git Agent;
- Browser Agent;
- Email Agent;
- Calendar Agent;
- Book Agent;
- Salesforce Agent;
- Home Assistant Agent.

The first implemented agent will be the Vault Agent.

The Vault Agent is responsible only for operations on Markdown notes.
It must not run Linux commands, browse the web, manage Git or access email.

### Actions

Actions are workflows.

An action may combine multiple tools to accomplish a higher-level task.

Example:

```text
create_daily_note
  ↓
search note
  ↓
create note if missing
  ↓
append template
  ↓
verify file exists
```

Actions are not primitive operations.
They encode domain workflows.

### Tools

Tools perform one real operation.

Examples:

- read_note;
- write_note;
- append_note;
- search_notes;
- run_command;
- git_status;
- docker_logs;
- ocr_pdf.

A tool must not pretend to execute.
A tool either succeeds, fails or returns an explicit partial result.
Every tool result must be inspectable.

#### Vault folder operations

The VaultAgent supports controlled folder operations inside the configured Vault path.

Supported folder operations:

- `list_folders`
- `create_folder`
- `delete_folder`

These operations are scoped to the Vault domain and must not be treated as generic filesystem commands.

`list_folders` is read-only.

`create_folder` and `delete_folder` are write operations and require explicit confirmation when executed through the LLM proposal flow.

`delete_folder` only deletes empty folders and refuses to delete the Vault root, files, symlinks, paths outside the Vault, or non-empty folders.

#### Tool rule

The assistant must never claim that a file was modified unless the corresponding tool successfully executed.

Every modification should follow this pattern:

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

Verification is not optional for write operations.

### Resources

Resources are external systems or data sources operated on by tools.

Examples:

- Vault;
- filesystem;
- Git repositories;
- Docker;
- Linux system;
- browser;
- email;
- calendar;
- PDFs;
- images;
- books.

Resources are not part of the assistant itself.
They are controlled through tools.

### LLM

The LLM is replaceable.

The first provider is Ollama.

The architecture must allow future providers without changing agent logic.

The LLM may be used for:

- interpreting requests;
- selecting tools;
- generating text;
- summarizing results;
- classifying content.

The LLM must not be treated as proof of execution.
Only tools can execute.

## Memory

Memory is divided into layers.

### Long-term memory

The Vault.

This is the durable source of truth.

### Working memory

Runtime state used during execution.

It may be stored under `var/state/`.

It is not part of the repository.

### Conversation memory

The current interaction context.

It is temporary.

### Configuration memory

User-specific paths and preferences.

These must be externalized and not committed if they contain personal data.

## Repository layout

```text
assistant/
├── app/
├── src/local_assistant/
├── prompts/
├── docs/
├── tests/
├── scripts/
├── examples/
├── experiments/
├── benchmarks/
├── var/
└── .github/
```

### Code location

Application code lives under:

```text
src/local_assistant/
```

The entrypoint lives under:

```text
app/main.py
```

### Documentation location

Project documentation lives under:

```text
docs/
```

Architecture decisions live under:

```text
docs/decisions/
```

Prompts live under:

```text
prompts/
```

Prompts are versioned because they are part of system behavior.

### Runtime data

Runtime data lives under:

```text
var/
```

The repository keeps only placeholder files such as `.gitkeep`.

The actual contents of `var/` are ignored by Git.

### External personal data

The real Vault, books, images, PDFs, models, embeddings and indexes must remain outside the repository.

The assistant should access them through configuration.

No personal knowledge base should be committed to this repository.
