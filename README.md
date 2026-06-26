# Local Assistant

Local Assistant is a long-term personal cognitive assistant designed to run locally and operate on user-owned knowledge and tools.

This project is not a chatbot.

The objective is to build a modular local cognitive layer capable of reading, searching, organizing and eventually acting on a personal digital environment while preserving privacy and architectural independence from any single model, tool, framework or user interface.

## Core idea

The assistant is composed of separate layers:

```text
Human
  ↓
CLI / UI
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

The LLM is one replaceable component used by agents and the orchestrator to reason, interpret and generate language.

## Main principles

- Privacy first.
- Local by default.
- Cloud optional, never required.
- Markdown Vault as the long-term source of truth.
- Tools perform real operations.
- No fake execution.
- Every write operation must be verifiable.
- Components must remain replaceable.
- Documentation is part of the product.

## Current status

The project currently provides a structured CLI for Markdown Vault operations.

Available Vault tools:

| Command | Operation |
| --- | --- |
| `read-note` | Read a Markdown note |
| `search-notes` | Search text inside Markdown notes |
| `append-note` | Append content to an existing note |
| `write-note` | Create or overwrite a note |

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

The CLI is structured and explicit.

It does not yet provide free-form natural language interaction.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

After installation, the CLI command is available:

```bash
local-assistant --help
```

## Configuration

Configuration is read from environment variables.

Example values are documented in:

```text
.env.example
```

The most important variable is:

```bash
LOCAL_ASSISTANT_VAULT_PATH=/path/to/your/vault
```

Example:

```bash
LOCAL_ASSISTANT_VAULT_PATH=/home/user/Vault \
local-assistant search-notes "Salesforce"
```

You can also override the Vault path per command:

```bash
local-assistant \
  --vault-path examples/sample_vault \
  search-notes Vault
```

## CLI usage

### Read a note

```bash
local-assistant \
  --vault-path examples/sample_vault \
  read-note welcome.md
```

### Search notes

```bash
local-assistant \
  --vault-path examples/sample_vault \
  search-notes Vault
```

### Write a new note

```bash
local-assistant \
  --vault-path examples/sample_vault \
  write-note ideas/new-note.md "# New Note"
```

By default, `write-note` refuses to overwrite existing notes.

To overwrite explicitly:

```bash
local-assistant \
  --vault-path examples/sample_vault \
  write-note ideas/new-note.md "# Updated Note" \
  --overwrite
```

### Append to an existing note

```bash
local-assistant \
  --vault-path examples/sample_vault \
  append-note ideas/new-note.md "
Appended content."
```

### Use a content file

```bash
local-assistant \
  --vault-path examples/sample_vault \
  write-note ideas/from-file.md \
  --content-file /tmp/content.md
```

### JSON output

```bash
local-assistant \
  --json \
  --vault-path examples/sample_vault \
  read-note welcome.md
```

## Repository scope

This repository contains:

- source code;
- prompts;
- documentation;
- architecture decisions;
- tests;
- examples;
- experiments;
- benchmark definitions.

It does not contain:

- the real Obsidian Vault;
- personal documents;
- PDFs;
- images;
- books;
- models;
- embeddings;
- indexes;
- runtime databases;
- logs.

Personal data must live outside the repository and be referenced through configuration.

## Development

Run the full test suite:

```bash
python -m pytest
```

Expected result at the current stage:

```text
59 passed
```

The exact number may increase as the project grows, but the suite must pass before merging feature branches.

## Current milestone

The first milestone is a minimal Vault Assistant capable of:

- reading Markdown notes;
- searching Markdown notes;
- appending content to notes;
- writing notes;
- verifying file modifications;
- exposing those operations through a structured CLI.

This milestone is now mostly implemented.

The next stage is not full chat.

The next stage is controlled LLM-assisted intent parsing: transforming a natural language request into a proposed structured command before execution.
