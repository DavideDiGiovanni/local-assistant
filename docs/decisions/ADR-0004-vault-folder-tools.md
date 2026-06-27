# ADR-0004: Vault folder tools

## Status

Accepted

## Context

The assistant now supports controlled operations on Markdown notes inside the Vault.

The next required capability is basic folder management, so the Vault can be structured without exposing generic filesystem operations.

The Vault is a domain boundary. Folder operations must therefore be implemented as Vault operations, not as Linux-like commands.

## Decision

Introduce three Vault folder operations:

- `list_folders`
- `create_folder`
- `delete_folder`

`list_folders` is a read operation and does not require confirmation.

`create_folder` is a write operation and requires confirmation when proposed through the LLM flow.

`delete_folder` is a write operation and requires confirmation when proposed through the LLM flow.

`delete_folder` is intentionally conservative:

- it can only delete folders inside the Vault;
- it cannot delete the Vault root;
- it cannot delete files;
- it cannot delete symlinks;
- it cannot delete non-empty folders;
- it rejects path traversal;
- it verifies deletion after execution.

The LLM may only propose these operations as structured CommandProposal data. The system validates the proposal before execution. Write operations remain gated by explicit confirmation.

## Consequences

The assistant can now help structure the Vault without exposing arbitrary filesystem access.

Folder deletion is safe by default and cannot behave like `rm -rf`.

Moving or renaming notes and folders is intentionally not included in this ADR. Those operations may affect Markdown links, wikilinks, backlinks and Obsidian-style references, so they require a separate design decision.

## Non-goals

This ADR does not introduce:

- generic filesystem operations;
- recursive folder deletion;
- note or folder moving;
- automatic link rewriting;
- Obsidian-specific backlink management;
- autonomous multi-step reorganization.
