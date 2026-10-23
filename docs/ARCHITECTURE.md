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
| `app/ai/activity_classifier.py` | C | Vision-based three-state result using the configured provider |
| `app/ai/resume_anchor.py` | C | Evidence-based resume anchor from recent history |
| `app/ui`, notifications, integration | D | PyQt UI and Windows delivery |

## Public contracts

```python
ContextProvider.capture(task: str) -> ContextSnapshot
ActivityClassifier.classify(context: ContextSnapshot) -> ClassificationResult
ResumeAnchorGenerator.generate(task: str, history: list[HistoryEvent]) -> ResumeAnchor
LLMClient.analyze(image: bytes, prompt: str, context: dict | None = None) -> dict
```

Do not redefine schemas or write screenshots to session storage.

The UI dispatches classification away from the Qt event loop. Results from a
stopped or replaced session are discarded before they can enter session history.
