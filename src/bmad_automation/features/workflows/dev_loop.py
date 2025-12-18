"""Development loop workflow using LoopAgent."""

from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from bmad_automation.shared.consts import REVIEW_STATUS_PASS


class ReviewCheckAgent(BaseAgent):
    """Escalates to exit loop when review passes."""

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event]:
        """Check review result and escalate if passed."""
        result = ctx.session.state.get("review_result", {})
        should_stop = result.get("status") == REVIEW_STATUS_PASS
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


def create_dev_loop(
    impl_agent: LlmAgent,
    review_agent: LlmAgent,
    max_iterations: int = 3,
) -> LoopAgent:
    """Create a development loop with implementation and review."""
    return LoopAgent(
        name="DevelopmentLoop",
        max_iterations=max_iterations,
        sub_agents=[
            impl_agent,
            review_agent,
            ReviewCheckAgent(name="ReviewCheck"),
        ],
    )
