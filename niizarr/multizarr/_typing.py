from __future__ import annotations

"""
Compatibility helpers for typing-related features that moved or were added
across Python versions.
"""

from typing import Any

JSON = Any

try:
    from pydantic.dataclasses import dataclass
except ImportError:
    from dataclasses import dataclass

try:  # Python < 3.10 compatibility
    from typing import TypeAlias, Unpack
except ImportError:
    from typing_extensions import TypeAlias, Unpack

__all__ = ["TypeAlias", "Unpack", "JSON", "dataclass"]

