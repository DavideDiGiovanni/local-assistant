# ADR-0001: Baseline Architecture

## Status

Accepted.

## Date

2026-06-26

## Context

The project aims to build a long-term local personal cognitive assistant.

The system is not intended to be a chatbot, an Obsidian plugin or a wrapper around a specific language model.

The assistant should eventually operate on notes, files, PDFs, images, books, repositories, logs, browser sessions, emails and other local or self-hosted resources.

Privacy is mandatory.

Cloud services may be optional adapters but must not be required.

The architecture must remain valid if individual components are replaced.

Examples of replaceable components:

- Obsidian;
- Ollama;
- the language model;
- the orchestration framework;
- the user interface;
- indexing systems;
- embedding systems.

## Decision

Adopt a layered architecture:

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

The LLM is not the assistant.
The LLM is a replaceable provider used by the orchestrator and agents.

Tools are the only components allowed to perform real operations.

Agents own domains.

The orchestrator routes work and coordinates agents but does not know implementation details of tools.

The first implemented domain will be the Vault domain.

The first milestone is a minimal Vault Agent capable of:

- connecting to Ollama;
- reading Markdown notes;
- searching Markdown notes;
- appending Markdown notes;
- writing Markdown notes;
- verifying modifications.

All other domains are postponed.

### Repository decision

Use a single monorepo for the initial phase.

The repository contains:

- source code;
- prompts;
- documentation;
- architecture decisions;
- tests;
- examples;
- experiments;
- benchmarks.

The repository does not contain personal data.

Runtime artifacts are stored under `var/` and ignored by Git, except for placeholder `.gitkeep` files.

Real Vaults, PDFs, images, books, models, embeddings and indexes must stay outside the repository.

## Consequences

### Positive consequences

- clear separation of responsibilities;
- replaceable model provider;
- replaceable user interface;
- inspectable tool execution;
- lower risk of hallucinated actions;
- documentation remains aligned with architecture;
- the project can grow gradually.

### Negative consequences

- slower initial development;
- more boilerplate than a quick prototype;
- fewer immediate features;
- more discipline required when adding components.

## Alternatives considered

### Build directly as an Obsidian plugin

Rejected.

Obsidian should be one possible interface, not the assistant itself.
The assistant must survive if Obsidian is replaced.

### Use a large agent framework immediately

Rejected for the first milestone.

Frameworks may become useful later, but introducing them before the first tool works would hide important architectural details.

### Treat the LLM as the orchestrator

Rejected.

The LLM may help decide, but orchestration must remain an explicit architectural layer.
Tool execution must be real, inspectable and verifiable.

### Store all knowledge in embeddings

Rejected.

Embeddings are derived artifacts.
The Vault remains the durable source of truth.
Indexes and embeddings must be rebuildable.

## Validation

This decision is valid if the first milestone can be implemented with:

- one replaceable LLM provider;
- one Vault Agent;
- a small set of real Vault tools;
- verified write operations;
- tests for tool behavior;
- no dependency on Obsidian internals.
