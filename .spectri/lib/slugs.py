"""Filename generation utilities for Spectri.

Python equivalent of filename-utils.sh. Provides slugify for kebab-case conversion.
"""

from __future__ import annotations

import re


def slugify(text: str) -> str:
    """Convert a string to a lowercase kebab-case slug.

    Steps: lowercase -> non-alphanumeric to hyphens -> collapse multiples -> trim edges

    >>> slugify("Hello World Test")
    'hello-world-test'
    >>> slugify("API Gateway v2.0")
    'api-gateway-v2-0'
    >>> slugify("already-kebab-case")
    'already-kebab-case'
    """
    result = text.lower()
    result = re.sub(r"[^a-z0-9]", "-", result)
    result = re.sub(r"-{2,}", "-", result)
    result = result.strip("-")
    return result
