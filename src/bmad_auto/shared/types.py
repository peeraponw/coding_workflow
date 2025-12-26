"""Shared type aliases for bmad-auto.

Type aliases for common patterns used across the codebase.
"""

from typing import TypeAlias

# Story identifiers
StoryId: TypeAlias = str
StoryKey: TypeAlias = str

# Epic identifiers
EpicKey: TypeAlias = str
EpicPath: TypeAlias = str

# Agent and phase
AgentId: TypeAlias = str
Phase: TypeAlias = str

# Status
StoryStatus: TypeAlias = str

# Workflow state
WorkflowState: TypeAlias = dict
