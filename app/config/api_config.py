"""Environment-first LLM configuration for FlowGuard."""

import os
from dataclasses import dataclass
from enum import Enum

try:
    from dotenv import load_dotenv
except ImportError:  # The application still works with ordinary environment variables.
    load_dotenv = None


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


@dataclass(frozen=True)
class APISettings:
    provider: LLMProvider
    api_key: str
    model: str
    base_url: str
    timeout_seconds: float = 30.0
    max_dimension: int = 1024
    jpeg_quality: int = 85
    max_image_size_mb: int = 4

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    @classmethod
    def from_env(cls) -> "APISettings":
        """Read configuration without ever writing credentials to disk."""
        if load_dotenv:
            load_dotenv()
        try:
            provider = LLMProvider(os.getenv("FLOWGUARD_LLM_PROVIDER", "openai").lower())
        except ValueError as exc:
            raise ValueError("FLOWGUARD_LLM_PROVIDER must be 'openai' or 'gemini'.") from exc

        if provider is LLMProvider.OPENAI:
            return cls(
                provider=provider,
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
                timeout_seconds=float(os.getenv("FLOWGUARD_LLM_TIMEOUT", "30")),
            )

        return cls(
            provider=provider,
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            base_url="https://generativelanguage.googleapis.com",
            timeout_seconds=float(os.getenv("FLOWGUARD_LLM_TIMEOUT", "30")),
        )
