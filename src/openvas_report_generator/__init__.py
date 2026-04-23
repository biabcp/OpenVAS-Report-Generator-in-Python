"""OpenVAS report generator package."""

from .client import OpenVASClient
from .config import OpenVASConfig

__all__ = ["OpenVASClient", "OpenVASConfig"]
