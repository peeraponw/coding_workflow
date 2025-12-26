"""Claude Agent SDK adapter implementing AgentProtocol.

Provides a uniform interface for invoking Claude-based agents.
"""

from bmad_auto.agents.base import AgentResult


class ClaudeAgent:
    """Claude Agent SDK wrapper implementing AgentProtocol.

    This adapter invokes Claude agents via skill commands (not raw prompts).
    State is managed externally by the orchestrator - this adapter is stateless.

    Attributes:
        working_dir: Directory for agent execution (typically project root)
        use_logged_in: If True, use logged-in Claude Code credentials
        api_key: Optional API key for headless execution
    """

    def __init__(
        self,
        working_dir: str,
        use_logged_in: bool = True,
        api_key: str | None = None,
    ) -> None:
        """Initialize Claude agent.

        Args:
            working_dir: Working directory for agent execution
            use_logged_in: Use Claude Code desktop credentials (default True)
            api_key: Optional API key for headless execution

        Raises:
            ValueError: If neither use_logged_in nor api_key is provided
        """
        if not use_logged_in and not api_key:
            raise ValueError("Either use_logged_in=True or api_key must be provided")

        self.working_dir = working_dir
        self.use_logged_in = use_logged_in
        self.api_key = api_key

    async def run(self, command: str) -> AgentResult:
        """Execute agent command via Claude Agent SDK.

        Args:
            command: Agent skill command (e.g., "/bmad:bmm:agents:sm create stories")

        Returns:
            AgentResult with success status and output

        Raises:
            AgentError: If SDK execution fails critically
        """
        try:
            from claude_agent_sdk import ClaudeAgentOptions, query

            # Build SDK options - pass api_key via env for headless execution
            if self.api_key:
                options = ClaudeAgentOptions(
                    permission_mode="acceptEdits",  # type: ignore[arg-type]
                    cwd=self.working_dir,
                    env={"ANTHROPIC_API_KEY": self.api_key},
                )
            else:
                options = ClaudeAgentOptions(
                    permission_mode="acceptEdits",  # type: ignore[arg-type]
                    cwd=self.working_dir,
                )

            # Execute command and collect output
            output_parts: list[str] = []
            result = ""

            async for message in query(prompt=command, options=options):
                msg_type = message.type  # type: ignore[attr-defined]
                if msg_type == "content":
                    # Content delta during execution
                    if hasattr(message, "delta"):
                        output_parts.append(message.delta)  # type: ignore[attr-defined]
                elif msg_type == "result":
                    # Final result message
                    result = message.result  # type: ignore[attr-defined]
                elif msg_type == "error":
                    # Error from SDK
                    error_val = message.error if hasattr(message, "error") else "Agent execution failed"  # type: ignore[attr-defined]
                    return AgentResult.fail(error=str(error_val))

            # Combine stream output with final result
            full_output = "\n".join(output_parts)
            if result:
                full_output = f"{full_output}\n{result}".strip()

            return AgentResult.ok(full_output if full_output else "Command executed")

        except Exception as e:
            # Map SDK exceptions to AgentResult.fail()
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                error_msg = "Authentication failed. Check API key or use_logged_in setting."
            elif "rate" in error_msg.lower():
                error_msg = f"Rate limit exceeded: {error_msg}"
            elif "timeout" in error_msg.lower():
                error_msg = f"Request timeout: {error_msg}"

            return AgentResult.fail(error_msg)
