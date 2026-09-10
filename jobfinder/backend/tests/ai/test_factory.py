"""Tests for the AI provider factory (env-driven provider selection)."""

import pytest

from app.ai.factory import get_ai_provider
from app.ai.fake_provider import FakeProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.openai_provider import OpenAIProvider


class TestGetAIProvider:
    def test_explicit_fake(self):
        assert isinstance(get_ai_provider("fake"), FakeProvider)

    def test_explicit_ollama_uses_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://example:1234")
        monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
        provider = get_ai_provider("ollama")
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://example:1234"
        assert provider.get_model() == "llama3.2"

    def test_explicit_openai_uses_env(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        provider = get_ai_provider("openai")
        assert isinstance(provider, OpenAIProvider)
        assert provider.get_model() == "gpt-4o"
        assert provider.api_key == "sk-test"

    def test_reads_ai_provider_env(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "fake")
        assert isinstance(get_ai_provider(), FakeProvider)

    def test_defaults_to_ollama(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        assert isinstance(get_ai_provider(), OllamaProvider)

    def test_case_and_whitespace_insensitive(self):
        assert isinstance(get_ai_provider("  Fake "), FakeProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            get_ai_provider("gemini")
