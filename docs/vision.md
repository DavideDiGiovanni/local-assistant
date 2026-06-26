# Vision

## Purpose

The purpose of this project is to build a local personal cognitive assistant.

The assistant should become an external cognitive layer able to understand, organize and operate on a personal digital environment.

It is not meant to be a simple chatbot, an Obsidian plugin or a wrapper around a language model.

The long-term goal is a system that can help manage knowledge, files, projects, notes, repositories, documentation, logs, books, images, transcripts and future automation systems while remaining private and user-controlled.

## Core philosophy

The architecture must separate responsibilities clearly:

```text
OS != Assistant
LLM != Agent
Agent != Tool
Tool != Memory
Memory != UI
```

No individual component should be treated as permanent.

- Obsidian may be replaced.
- Ollama may be replaced.
- The orchestration framework may be replaced.
- The language model will almost certainly be replaced.

The architecture must survive these changes.

## Source of truth

The long-term source of truth is the Vault.

The Vault is composed of Markdown files and user-owned knowledge.

Everything else is derived:

- embeddings;
- indexes;
- caches;
- summaries;
- temporary state;
- generated views;
- runtime databases.

Derived artifacts must be rebuildable.

The Vault must remain portable, readable and independent from the assistant.

## Privacy

Privacy is mandatory.

The assistant should preferably run locally.

Cloud services may be introduced only as optional adapters, never as required infrastructure.

No personal data should be committed to the repository.

No tool should transmit user data externally unless that behavior is explicit, configurable and documented.

## Long-term scope

The assistant should eventually understand and operate on:

- Markdown notes;
- Obsidian Vaults;
- PDF manuals;
- scanned PDFs through OCR;
- images and screenshots;
- books and Calibre libraries;
- Git repositories;
- Linux filesystem;
- Docker;
- system logs;
- browser sessions;
- emails;
- recordings and transcripts;
- technical documentation;
- Home Assistant;
- Salesforce projects;
- programming projects.

The objective is not only search.
The objective is understanding, organization and action.

## Multimodal direction

Nothing should remain opaque.

- Images should become descriptions, classifications and searchable knowledge.
- Scanned PDFs should become OCR text, structured notes and searchable knowledge.
- Audio and video should become transcripts, summaries and searchable knowledge.

The system should progressively transform opaque media into structured, inspectable information.

## Self-hosting direction

In the long term, the assistant should help develop itself.

It should be able to:

- read its own documentation;
- understand its architecture;
- suggest new tools;
- generate code;
- update documentation;
- create tests;
- propose local pull requests.

This must happen gradually and only after the foundational layers are reliable.
