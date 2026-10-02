# FlowGuard architecture

## Purpose

FlowGuard is a Windows task-detour and interruption-recovery assistant. A user declares a task; later milestones collect active-window context, classify it, retain a local event history, and generate a resume anchor.

## Stable pipeline

```text
ContextProvider -> ActivityClassifier -> SessionStore -> ResumeAnchorGenerator -> callback/UI
```

`ContextSnapshot.screenshot` is in-memory only. `SessionStore` persists only task metadata and `HistoryEvent` records below `~/.flowguard/sessions/`.

## Ownership

| Layer | Owner | Contract |
|---|---|---|
| `app/core` | A | Stable data models and protocols |
| `app/ai/llm_client.py` | A | Provider-agnostic `LLMClient.analyze()` |
| `app/storage` | A | JSON session lifecycle |
| `app/capture` | A | Primary-screen JPEG bytes |
| `app/context` | B | Windows foreground context and event trigger |
| `app/ai/{classifier,resume_anchor}` | C | Three-way result and truthful resume anchor |
| `app/ui`, notifications, integration | D | PyQt UI and Windows delivery |

## Public contracts

```python
ContextProvider.capture(task: str) -> ContextSnapshot
ActivityClassifier.classify(context: ContextSnapshot) -> ClassificationResult
ResumeAnchorGenerator.generate(task: str, history: list[HistoryEvent]) -> ResumeAnchor
LLMClient.analyze(image: bytes, prompt: str, context: dict | None = None) -> dict
```

Do not redefine schemas or write screenshots to session storage.
