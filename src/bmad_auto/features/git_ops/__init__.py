"""Git operations feature package."""

from .manager import GitManager
from .models import GitConfig

__all__ = ["GitManager", "GitConfig"]
