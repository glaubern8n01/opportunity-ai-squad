"""Plugin de provedor de IA: Anthropic (Claude)."""

from __future__ import annotations

from typing import Any

import anthropic

from opportunity_squad.core.exceptions import AIProviderError, ConfigurationError
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def initialize(self, config: dict[str, Any]) -> None:
        api_key = config.get("api_key")
        if not api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY não configurada")

        self._client = anthropic.Anthropic(api_key=api_key)
        self._models = {
            ModelTier.CHEAP: config.get("model_cheap", "claude-haiku-4-5"),
            ModelTier.STANDARD: config.get("model_standard", "claude-sonnet-5"),
            ModelTier.DEEP: config.get("model_deep", "claude-opus-4-8"),
        }

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        tier: ModelTier = ModelTier.STANDARD,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> str:
        model = self._models[tier]
        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise AIProviderError(f"Anthropic API falhou ({model}): {exc}") from exc

        return "".join(
            getattr(block, "text", "") for block in response.content if block.type == "text"
        )

    def shutdown(self) -> None:
        self._client.close()
