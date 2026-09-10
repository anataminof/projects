"""Factory for selecting an AI provider from environment configuration.

The dev scripts (``start-dev-<provider>.sh``) export ``AI_PROVIDER`` plus the
provider-specific variables from ``.env.local``. ``get_ai_provider()`` reads
those and returns a ready-to-use :class:`AIProvider`.

Recognised environment variables
--------------------------------
AI_PROVIDER        one of: ``ollama`` (default), ``openai``, ``fake``
OLLAMA_BASE_URL    Ollama server URL          (default ``http://127.0.0.1:11434``)
OLLAMA_MODEL       Ollama model name          (default ``mistral:7b``)
OPENAI_API_KEY     OpenAI API key             (required for the ``openai`` provider)
OPENAI_MODEL       OpenAI chat model          (default ``gpt-4o-mini``)
OPENAI_BASE_URL    optional custom API base URL
"""

import os
from typing import Optional

from .provider import AIProvider

VALID_PROVIDERS = ("ollama", "openai", "fake")


def get_ai_provider(name: Optional[str] = None) -> AIProvider:
    """
    Build an :class:`AIProvider` from ``name`` or the ``AI_PROVIDER`` env var.

    Args:
        name: Explicit provider name. When ``None``, ``AI_PROVIDER`` is used,
            falling back to ``"ollama"``.

    Returns:
        A configured provider instance.

    Raises:
        ValueError: if the provider name is not recognised.
    """
    provider = (name or os.getenv("AI_PROVIDER") or "ollama").strip().lower()

    if provider == "fake":
        from .fake_provider import FakeProvider
        return FakeProvider()

    if provider == "ollama":
        from .ollama_provider import OllamaProvider
        return OllamaProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            model=os.getenv("OLLAMA_MODEL", "mistral:7b"),
        )

    if provider == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )

    raise ValueError(
        f"Unknown AI_PROVIDER {provider!r}; expected one of {', '.join(VALID_PROVIDERS)}"
    )
