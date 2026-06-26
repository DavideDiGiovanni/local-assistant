# Local Assistant

Local Assistant is a long-term personal cognitive assistant designed to run locally and operate on user-owned knowledge and tools.

This project is not a chatbot.

The objective is to build a modular local cognitive layer capable of reading, searching, organizing and eventually acting on a personal digital environment while preserving privacy and architectural independence from any single model, tool, framework or user interface.

## Core idea

The assistant is composed of separate layers:

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

## Current milestone

The first milestone is a minimal Vault Agent capable of:

- connecting to Ollama;
- reading Markdown notes;
- searching Markdown notes;
- appending content to notes;
- writing notes;
- verifying file modifications.

No browser automation, OCR, email, Linux administration, Git automation or multi-agent orchestration will be added before the first Vault Agent works reliably.

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

## Status

Baseline architecture: v1.

The structure is intentionally conservative. The goal is to validate each layer before adding complexity.
