"""Active extraction configuration shared by the app and provider verification tools.

The older direct-patch adapter remains in gemini.py for historical comparisons;
there is no automatic fallback to it.
"""

from .gemini import ENDPOINT, MODEL
from .gemini_decisions import (
    FieldDecisionExtractor as GeminiExtractor,
    PROMPT,
    PROMPT_VERSION,
    SCHEMA_VERSION,
    build_decision_request as build_request,
    decision_schema as extraction_schema,
)

__all__ = [
    "ENDPOINT",
    "MODEL",
    "GeminiExtractor",
    "PROMPT",
    "PROMPT_VERSION",
    "SCHEMA_VERSION",
    "build_request",
    "extraction_schema",
]
