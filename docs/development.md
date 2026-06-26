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

## Branching

Use `main` for stable code.

Use `develop` for active development.

Feature work should happen on dedicated branches from `develop`.

Suggested flow:

```bash
git switch develop
git switch -c feature/vault-read-note
```

Merge feature branches back into `develop`.

Merge `develop` into `main` only when the milestone is stable.

## Commit style

Prefer small commits.

Each commit should represent one meaningful change.

Examples:

```text
Add baseline architecture documentation
Add Ollama provider interface
Add read_note tool
Add tests for missing note handling
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
/home/dave/Documents/Vault
```

Valid approach:

Read the Vault path from configuration.

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

Tests should be introduced from the first real tool.

Minimum expected tests for tools:

- success case;
- missing input;
- invalid path;
- permission or write failure where applicable;
- verification failure where applicable.

The first integration tests should use a sample Vault under `examples/`.

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

Until the first milestone is complete, do not focus on:

- large models;
- prompt optimization;
- context compression;
- embeddings;
- vector databases;
- advanced RAG;
- multimodal processing;
- orchestration frameworks;
- multi-agent collaboration.

The immediate goal is a working and verifiable Vault Agent.
