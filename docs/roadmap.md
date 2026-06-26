# Roadmap

## Method

The project must progress one validated layer at a time.

The rule is:

```text
Do not add the next layer until the current layer works and is verified.
```

The system should grow slowly and remain understandable.

## Phase 0: Repository and documentation

Status: in progress.

Goals:

- create the repository;
- define the baseline structure;
- document the vision;
- document the architecture;
- record the first architecture decision;
- define the first milestone.

Exit criteria:

- repository initialized;
- baseline files committed;
- documentation present;
- branch strategy available.

## Phase 1: LLM connection

Goal:

Connect the application to Ollama through a replaceable provider interface.

Scope:

- minimal Ollama client;
- simple prompt;
- simple response;
- no tools;
- no agent behavior.

Exit criteria:

- the application can send a prompt to Ollama;
- the response is printed;
- the LLM provider is isolated behind an interface.

## Phase 2: First tool

Goal:

Implement one real tool: `read_note`.

Scope:

- read a Markdown file from a configured Vault path;
- return a structured result;
- handle missing files;
- handle invalid paths;
- avoid hardcoded personal paths.

Exit criteria:

- tool reads an existing note;
- tool fails cleanly on missing note;
- tests cover success and failure;
- no fake execution.

## Phase 3: Vault write tools

Goal:

Add minimal write operations.

Tools:

- append_note;
- write_note;
- search_notes.

Exit criteria:

- append modifies a note and verifies the result;
- write creates or overwrites a note and verifies the result;
- search returns real Markdown matches;
- all write operations are verified;
- tests cover tool behavior.

## Phase 4: Vault Agent

Goal:

Create the first domain agent.

Responsibilities:

- understand requests related to Markdown notes;
- select the correct Vault tool;
- execute the tool;
- verify results;
- produce a clear response.

Non-goals:

- no Linux commands;
- no browser access;
- no OCR;
- no Git actions;
- no email;
- no calendar;
- no multi-agent orchestration.

Exit criteria:

- the Vault Agent can read, search, append and write notes;
- the agent does not claim actions it did not perform;
- tool results are visible and inspectable.

## Phase 5: Minimal orchestrator

Goal:

Introduce the orchestrator only after the Vault Agent works.

Scope:

- route Vault-related requests to the Vault Agent;
- reject unsupported domains explicitly;
- keep implementation simple.

Exit criteria:

- orchestrator routes requests;
- unsupported requests are handled safely;
- no additional agents are introduced yet.

## Phase 6: Test and hardening

Goal:

Make the first milestone reliable.

Scope:

- unit tests;
- integration tests on a sample Vault;
- error handling;
- logging;
- configuration validation;
- documentation updates.

Exit criteria:

- repeatable test suite;
- documented setup;
- documented tool contracts;
- stable first milestone.

## Future phases

Only after the first milestone is stable, evaluate:

- Git Agent;
- Linux Agent;
- PDF and OCR tools;
- image understanding;
- Calibre integration;
- browser tools;
- email tools;
- calendar tools;
- Home Assistant tools;
- Salesforce project tools;
- embeddings;
- vector search;
- advanced RAG;
- orchestration frameworks.

These are intentionally postponed.
