"""Small cross-platform vision LLM client.

Image preparation and provider request flow are adapted from INA's MIT-licensed
``src/utils/direct_llm_client.py``. FlowGuard removes INA's py2app/macOS code
and exposes only the stable ``analyze`` interface.
"""

import base64
import io
import json
import re
from typing import Any

import requests
from PIL import Image

from app.config.api_config import APISettings, LLMProvider


class LLMClient:
    def __init__(self, settings: APISettings | None = None) -> None:
        self.settings = settings or APISettings.from_env()

    def prepare_image_for_api(self, image: bytes) -> tuple[bytes, str]:
        """Resize and JPEG-compress an in-memory screenshot for a vision API."""
        try:
            source = Image.open(io.BytesIO(image))
            if source.mode != "RGB":
                source = source.convert("RGB")

            if max(source.size) > self.settings.max_dimension:
                source.thumbnail(
                    (self.settings.max_dimension, self.settings.max_dimension),
                    Image.Resampling.LANCZOS,
                )

            compressed = self._encode_jpeg(source, self.settings.jpeg_quality)
            max_size = self.settings.max_image_size_mb * 1024 * 1024
            for quality in (70, 50, 30):
                if len(compressed) <= max_size:
                    break
                compressed = self._encode_jpeg(source, quality)
            if len(compressed) > max_size:
                raise ValueError("Screenshot remains larger than the configured API limit.")

            return compressed, base64.b64encode(compressed).decode("ascii")
        except Exception as exc:
            raise ValueError(f"Failed to process screenshot: {exc}") from exc

    @staticmethod
    def _encode_jpeg(image: Image.Image, quality: int) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        return buffer.getvalue()

    def analyze(self, image: bytes, prompt: str, context: dict | None = None) -> dict:
        """Send screenshot + prompt to the configured provider; return JSON-like data.

        Provider and parsing failures are returned as ``{"error": ...}`` so an
        event loop can continue monitoring instead of crashing the desktop app.
        """
        if not self.settings.is_configured:
            return {"error": "No API key configured for the selected provider."}
        try:
            compressed, base64_image = self.prepare_image_for_api(image)
            if self.settings.provider is LLMProvider.OPENAI:
                raw = self._analyze_openai(base64_image, prompt)
            else:
                raw = self._analyze_gemini(compressed, prompt)
            parsed = self._parse_json_response(raw)
            return {"data": parsed, "raw_response": raw, "context": context or {}}
        except Exception as exc:
            return {"error": str(exc), "context": context or {}}

    def test_api(self) -> dict:
        """Make a minimal provider request and return a non-throwing status."""
        if not self.settings.is_configured:
            return {"success": False, "message": "No API key configured."}
        try:
            if self.settings.provider is LLMProvider.OPENAI:
                text = self._request_openai_text("Reply with OK.")
            else:
                text = self._request_gemini_text("Reply with OK.")
            return {"success": bool(text), "message": text[:100]}
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    def _analyze_openai(self, base64_image: str, prompt: str) -> str:
        payload = {
            "model": self.settings.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3,
        }
        response = requests.post(
            f"{self.settings.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.settings.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _request_openai_text(self, prompt: str) -> str:
        payload = {
            "model": self.settings.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0,
        }
        response = requests.post(
            f"{self.settings.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.settings.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _analyze_gemini(self, image: bytes, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=self.settings.api_key)
        try:
            response = client.models.generate_content(
                model=self.settings.model,
                contents=[prompt, Image.open(io.BytesIO(image))],
            )
        finally:
            client.close()
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return response.text.strip()

    def _request_gemini_text(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=self.settings.api_key)
        try:
            response = client.models.generate_content(model=self.settings.model, contents=prompt)
        finally:
            client.close()
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return response.text.strip()

    @staticmethod
    def _parse_json_response(content: str) -> Any:
        """Parse plain JSON or a fenced JSON response while preserving text fallback."""
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", stripped, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {"text": content}
