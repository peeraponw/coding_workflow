"""Git integration module for bmad-auto.

This module provides GitHandler for centralized git CLI operations.
"""

from bmad_auto.features.git_integration.handler import GitHandler, GitError, GitStatus

__all__ = ["GitHandler", "GitError", "GitStatus"]
