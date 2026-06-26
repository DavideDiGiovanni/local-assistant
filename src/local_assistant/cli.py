import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from local_assistant.config.settings import load_settings
from local_assistant.models.orchestrator_result import OrchestratorResult
from local_assistant.orchestrator.orchestrator import Orchestrator


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    settings = load_settings()
    vault_path = Path(args.vault_path).expanduser() if args.vault_path else settings.vault_path

    orchestrator = Orchestrator(vault_path)

    result = execute_command(orchestrator, args)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_human_result(result)

    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-assistant",
        description="Structured CLI for the Local Assistant.",
    )

    parser.add_argument(
        "--vault-path",
        help="Path to the Markdown Vault. Overrides LOCAL_ASSISTANT_VAULT_PATH.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full structured result as JSON.",
    )

    subparsers = parser.add_subparsers(dest="command")

    read_parser = subparsers.add_parser(
        "read-note",
        help="Read a Markdown note from the Vault.",
    )
    read_parser.add_argument("relative_path")

    search_parser = subparsers.add_parser(
        "search-notes",
        help="Search text inside Markdown notes.",
    )
    search_parser.add_argument("query")

    append_parser = subparsers.add_parser(
        "append-note",
        help="Append content to an existing Markdown note.",
    )
    append_parser.add_argument("relative_path")
    append_parser.add_argument(
        "content",
        nargs="?",
        help="Content to append. Use quotes for spaces.",
    )
    append_parser.add_argument(
        "--content-file",
        help="Read content to append from a file.",
    )

    write_parser = subparsers.add_parser(
        "write-note",
        help="Create or overwrite a Markdown note.",
    )
    write_parser.add_argument("relative_path")
    write_parser.add_argument(
        "content",
        nargs="?",
        help="Content to write. Use quotes for spaces.",
    )
    write_parser.add_argument(
        "--content-file",
        help="Read content to write from a file.",
    )
    write_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing note.",
    )

    return parser


def execute_command(
    orchestrator: Orchestrator,
    args: argparse.Namespace,
) -> OrchestratorResult:
    if args.command == "read-note":
        return orchestrator.execute(
            domain="vault",
            operation="read_note",
            relative_path=args.relative_path,
        )

    if args.command == "search-notes":
        return orchestrator.execute(
            domain="vault",
            operation="search_notes",
            query=args.query,
        )

    if args.command == "append-note":
        content = resolve_content(args.content, args.content_file)

        return orchestrator.execute(
            domain="vault",
            operation="append_note",
            relative_path=args.relative_path,
            content=content,
        )

    if args.command == "write-note":
        content = resolve_content(args.content, args.content_file)

        return orchestrator.execute(
            domain="vault",
            operation="write_note",
            relative_path=args.relative_path,
            content=content,
            overwrite=args.overwrite,
        )

    return OrchestratorResult(
        success=False,
        message="Unsupported CLI command.",
        domain="cli",
        operation=args.command or "",
        error="UNSUPPORTED_CLI_COMMAND",
    )


def resolve_content(
    inline_content: str | None,
    content_file: str | None,
) -> str:
    if inline_content is not None and content_file is not None:
        raise ValueError("Use either inline content or --content-file, not both.")

    if content_file is not None:
        return Path(content_file).expanduser().read_text(encoding="utf-8")

    if inline_content is not None:
        return inline_content

    return ""


def print_human_result(result: OrchestratorResult) -> None:
    print(f"success: {result.success}")
    print(f"message: {result.message}")

    if result.error:
        print(f"error: {result.error}")

    if result.operation == "read_note" and result.success:
        print("--- content ---")
        print(result.data["content"])
        return

    if result.operation == "search_notes" and result.success:
        print(f"matches: {result.data['match_count']}")

        for match in result.data["matches"]:
            print(
                f"{match['relative_path']}:{match['line_number']}: "
                f"{match['line']}"
            )

        return

    if "relative_path" in result.data:
        print(f"path: {result.data['relative_path']}")

    if "created" in result.data:
        print(f"created: {result.data['created']}")

    if "overwritten" in result.data:
        print(f"overwritten: {result.data['overwritten']}")
