# Project plan

## Delivered by A

- Stable schemas and `Protocol` interfaces.
- In-memory primary-screen screenshot provider.
- OpenAI/Gemini client with image resize, JPEG compression, Base64, timeout, API test, and non-throwing error result.
- Local JSON session store with no screenshot persistence.
- Mock end-to-end controller and acceptance demo.

## Next P0: B

1. Implement `app/context/windows_context.py` using the contracts in `app.core`.
2. Add lightweight app/title polling and debounce before screenshot capture.
3. Do not modify A's schemas, `SessionStore`, or `LLMClient` public interface.

## Scope lock

No macOS APIs, login, cloud database, browser URL extraction, OCR, RAG, agents, automatic computer control, or long-term learning.
