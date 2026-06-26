from local_assistant.actions.execute_command_proposal import ExecuteCommandProposal
from local_assistant.llm.base_provider import BaseLLMProvider
from local_assistant.llm.command_proposer import CommandProposer
from local_assistant.models.ask_result import AskResult
from local_assistant.orchestrator.orchestrator import Orchestrator
from local_assistant.validation.command_proposal_validator import (
    CommandProposalValidator,
)


class ControlledAsk:
    """
    Controlled natural-language flow.

    The LLM proposes a command.
    The system validates it.
    Read-only operations may execute immediately.
    Write operations require explicit confirmation.
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        orchestrator: Orchestrator,
        validator: CommandProposalValidator | None = None,
    ) -> None:
        self.validator = validator or CommandProposalValidator()
        self.proposer = CommandProposer(
            llm_provider=llm_provider,
            validator=self.validator,
        )
        self.executor = ExecuteCommandProposal(
            orchestrator=orchestrator,
            validator=self.validator,
        )

    def run(
        self,
        request: str,
        confirm: bool = False,
    ) -> AskResult:
        proposal_result = self.proposer.propose(request)

        if not proposal_result.success:
            return AskResult(
                success=False,
                message=proposal_result.message,
                request=request,
                proposal=proposal_result.proposal,
                proposal_result=proposal_result,
                error=proposal_result.error,
                data=proposal_result.data,
            )

        if proposal_result.proposal is None:
            return AskResult(
                success=False,
                message="Command proposal was not produced.",
                request=request,
                proposal_result=proposal_result,
                error="MISSING_PROPOSAL",
            )

        proposal = proposal_result.proposal

        if self.validator.requires_confirmation(proposal) and not confirm:
            return AskResult(
                success=False,
                message="Confirmation is required before executing this proposal.",
                request=request,
                proposal=proposal,
                proposal_result=proposal_result,
                error="CONFIRMATION_REQUIRED",
                data={
                    "domain": proposal.domain,
                    "operation": proposal.operation,
                    "arguments": proposal.arguments,
                    "requires_confirmation": True,
                    "explanation": proposal.explanation,
                },
            )

        execution_result = self.executor.execute(
            proposal=proposal,
            confirm=confirm,
        )

        return AskResult(
            success=execution_result.success,
            message=execution_result.message,
            request=request,
            proposal=proposal,
            proposal_result=proposal_result,
            execution_result=execution_result,
            error=execution_result.error,
            data={
                "domain": proposal.domain,
                "operation": proposal.operation,
                "arguments": proposal.arguments,
                "requires_confirmation": proposal.requires_confirmation,
                "explanation": proposal.explanation,
                "execution": execution_result.data,
            },
        )
