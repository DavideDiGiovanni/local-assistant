import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from local_assistant.actions.controlled_ask import ControlledAsk
from local_assistant.actions.execute_command_proposal import ExecuteCommandProposal
from local_assistant.config.settings import AppSettings, load_settings
from local_assistant.llm.command_proposer import CommandProposer
from local_assistant.llm.ollama_provider import OllamaProvider
from local_assistant.models.ask_result import AskResult
from local_assistant.models.command_proposal import CommandProposalResult
from local_assistant.models.orchestrator_result import OrchestratorResult
from local_assistant.orchestrator.orchestrator import Orchestrator
from local_assistant.prompting.prompt_loader import PromptLoader


COMMAND_PROPOSAL_PROMPT = "system/command_proposal.md"


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    settings = load_settings()
    vault_path = Path(args.vault_path).expanduser() if args.vault_path else settings.vault_path

    orchestrator = Orchestrator(vault_path)

    try:
        result = execute_command(orchestrator, args, settings)
    except Exception as exc:
        print("success: False")
        print("message: Command failed before execution.")
        print(f"error: {type(exc).__name__}")
        print(f"details: {exc}")
        return 1

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

    propose_parser = subparsers.add_parser(
        "propose",
        help="Use the configured LLM to propose a structured command without executing it.",
    )
    propose_parser.add_argument("request")

    execute_proposal_parser = subparsers.add_parser(
        "execute-proposal",
        help="Execute a validated command proposal JSON file.",
    )
    execute_proposal_parser.add_argument("proposal_file")
    execute_proposal_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm execution of proposals that modify the Vault.",
    )

    ask_parser = subparsers.add_parser(
        "ask",
        help="Use the configured LLM to propose and safely execute a supported command.",
    )
    ask_parser.add_argument("request")
    ask_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Allow execution of proposals that modify the Vault.",
    )

    list_folders_parser = subparsers.add_parser(
        "list-folders",
        help="List folders inside the Vault.",
    )
    list_folders_parser.add_argument(
        "relative_path",
        nargs="?",
        default=".",
        help="Relative path inside the Vault. Defaults to Vault root.",
    )

    return parser


def execute_command(
    orchestrator: Orchestrator,
    args: argparse.Namespace,
    settings: AppSettings,
) -> OrchestratorResult | CommandProposalResult | AskResult:
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

    if args.command == "propose":
        llm_provider = build_llm_provider(settings)
        prompt_template = load_command_proposal_prompt(settings)
        proposer = CommandProposer(
            llm_provider=llm_provider,
            prompt_template=prompt_template,
        )

        return proposer.propose(args.request)

    if args.command == "execute-proposal":
        executor = ExecuteCommandProposal(orchestrator)

        return executor.execute_from_file(
            proposal_file=args.proposal_file,
            confirm=args.confirm,
        )

    if args.command == "ask":
        llm_provider = build_llm_provider(settings)
        prompt_template = load_command_proposal_prompt(settings)

        ask_action = ControlledAsk(
            llm_provider=llm_provider,
            prompt_template=prompt_template,
            orchestrator=orchestrator,
        )

        return ask_action.run(
            request=args.request,
            confirm=args.confirm,
        )

    if args.command == "list-folders":
        return orchestrator.execute(
            domain="vault",
            operation="list_folders",
            relative_path=args.relative_path,
        )

    return OrchestratorResult(
        success=False,
        message="Unsupported CLI command.",
        domain="cli",
        operation=args.command or "",
        error="UNSUPPORTED_CLI_COMMAND",
    )


def build_llm_provider(settings: AppSettings) -> OllamaProvider:
    if settings.llm_provider != "ollama":
        raise RuntimeError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    return OllamaProvider(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        timeout_seconds=settings.ollama_timeout_seconds,
    )


def load_command_proposal_prompt(settings: AppSettings) -> str:
    loader = PromptLoader(settings.prompts_path)
    return loader.load(COMMAND_PROPOSAL_PROMPT)


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


def print_human_result(
    result: OrchestratorResult | CommandProposalResult | AskResult,
) -> None:
    if isinstance(result, AskResult):
        print(f"success: {result.success}")
        print(f"message: {result.message}")

        if result.error:
            print(f"error: {result.error}")

        if result.proposal is not None:
            print("--- proposal ---")
            print(f"domain: {result.proposal.domain}")
            print(f"operation: {result.proposal.operation}")
            print(f"arguments: {result.proposal.arguments}")
            print(f"requires_confirmation: {result.proposal.requires_confirmation}")
            print(f"explanation: {result.proposal.explanation}")

        if result.execution_result is not None:
            print("--- execution ---")
            print_human_result(result.execution_result)

        return

    if isinstance(result, CommandProposalResult):
        print(f"success: {result.success}")
        print(f"message: {result.message}")

        if result.error:
            print(f"error: {result.error}")

        if result.proposal is not None:
            print(f"domain: {result.proposal.domain}")
            print(f"operation: {result.proposal.operation}")
            print(f"arguments: {result.proposal.arguments}")
            print(f"requires_confirmation: {result.proposal.requires_confirmation}")
            print(f"explanation: {result.proposal.explanation}")

        return

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

    if result.operation == "list_folders" and result.success:
        print(f"folders: {len(result.data['folders'])}")

        for folder in result.data["folders"]:
            print(folder["relative_path"])

        return

    if "relative_path" in result.data:
        print(f"path: {result.data['relative_path']}")

    if "created" in result.data:
        print(f"created: {result.data['created']}")

    if "overwritten" in result.data:
        print(f"overwritten: {result.data['overwritten']}")


def main() -> None:
    raise SystemExit(run_cli())
