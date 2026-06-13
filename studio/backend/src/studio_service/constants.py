"""Shared Plane card id constants for Studio runtime."""

from __future__ import annotations

import re

PLANE_CARD_PREFIX = "RPG"
PLANE_CARD_PATTERN = re.compile(r"^RPG-\d+$", re.IGNORECASE)
CARD_ID_RE = PLANE_CARD_PATTERN
DEFAULT_PLANE_CARD = "RPG-N"
