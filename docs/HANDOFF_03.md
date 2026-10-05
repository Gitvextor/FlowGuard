# FlowGuard Handoff 03

## Basic information

From: C
To: D
Date: 2026-10-05
Milestone: Three-way Classifier + Resume Engine

## Completed

- Implemented the three states `MAIN_TASK`, `NECESSARY_DETOUR`, and `DISTRACTION` using the shared `app.core` schemas.
- `ActivityClassifier` consumes a B-stage `ContextSnapshot` directly. It does not poll Windows, read another foreground window, or capture another screenshot.
- The classifier prompt includes the task, app, title, and the exact existing screenshot. It states that leaving the main app alone is not evidence of distraction and lowers confidence for ambiguous contexts.
- `ClassificationParser` validates raw response text as strict JSON, checks the exact four-field schema, validates the enum and field types, rejects empty/non-JSON/error responses, and clamps finite confidence values to `[0, 1]`.
- API exceptions, timeouts, HTTP errors, and parse failures return `MAIN_TASK` with `confidence=0.0` and `reason="Classification unavailable"`. Callers can read `classifier.last_error`; failure results are excluded from history by `to_history_event()`.
- Successful history summaries are extractive: they contain the observed app, observed title, and assigned classification. They do not persist the screenshot or model's free-form rationale.
- Added `FLOWGUARD_MOCK=true` support with simple deterministic cues for the fixed demo and 25 synthetic development cases spanning coding, writing, studying, research, messaging, and entertainment.
- Added a simple one/two-consecutive-distraction trigger helper and a conservative Resume Anchor based on the latest five recorded events. It uses the most recent `MAIN_TASK` record for `last_position`, explicitly reports an unknown problem when history has no verified issue, and suggests returning to the observed workspace.
- Added classifier and Resume Anchor prompts with v1 identifiers, the AI demo, tests, and this handoff.

## Public interfaces

```python
ActivityClassifier(client=None, parser=None, mock=None)
ActivityClassifier.classify(context: ContextSnapshot) -> ClassificationResult
ActivityClassifier.to_history_event(context, result) -> HistoryEvent | None
ClassificationParser.parse(response) -> ClassificationResult
ResumeAnchorGenerator.generate(task: str, history: list[HistoryEvent]) -> ResumeAnchor
should_generate_resume_anchor(history, consecutive_distractions=2) -> bool
```

Import C interfaces from `app.ai.classifier`, `app.ai.classifier_parser`, and `app.ai.resume_anchor`. Shared models and protocols remain defined only in `app.core`.

## Resume Anchor implementation note

The stable `ResumeAnchorGenerator.generate(task, history)` protocol receives only task text and `HistoryEvent` records. A's `LLMClient.analyze(image, prompt, context=None)` requires image bytes. C does not fabricate an image or add a second screenshot source for anchor generation: the anchor is therefore deterministic and evidence-bounded. `build_resume_anchor_prompt()` is versioned and available for a future text-only contract, but is not sent through the current vision-only client. `current_problem` remains explicitly unknown because the shared history schema does not record a verified unresolved problem.

## Demo

```powershell
python scripts/ai_demo.py
```

Expected states are `MAIN_TASK`, `NECESSARY_DETOUR`, and `DISTRACTION`, followed by a generated Resume Anchor and `AI ACCEPTANCE TEST: PASS`. It runs in mock mode and does not require an API key.

## Prompt versions

- Classifier: `classifier prompt v1`
- Resume: `resume prompt v1`

## Test cases and known weak spots

- `tests/data/ai_scenarios.json` contains 25 synthetic development cases. Tests cover the expected result for all cases, low confidence for ambiguous messaging/empty browser titles, parser errors and missing fields, invalid enum values, confidence clamping, timeout/API error fallback, extractive history, Resume Anchor grounding, and distraction streaks.
- Mock-mode keyword rules are only for offline UI development and demonstrations. They are not a substitute for the configured vision model and can mislabel unfamiliar or mixed-purpose titles.
- Messaging apps and blank browser titles remain semantically ambiguous. The mock path intentionally uses low confidence; a real model should combine task, app, title, and screenshot.
- Real model output quality, latency, rate limits, and provider-specific JSON adherence require a configured API key and were not tested with a paid API call.

## Validation

- Final interactive Windows acceptance after C: `FOUNDATION ACCEPTANCE TEST: PASS`; 43 tests passed; `WINDOWS CONTEXT ACCEPTANCE TEST: PASS`; `AI ACCEPTANCE TEST: PASS`.
- The agent's separate non-interactive session could not access the user's desktop (BitBlt screenshot failure; foreground reported `Unknown`/excluded); both desktop-dependent demos were rerun successfully in the interactive PowerShell session.
- No A or B implementation files were changed.

## D integration

```python
result = classifier.classify(snapshot)
event = classifier.to_history_event(snapshot, result)
if event is not None:
    session_store.append_event(event)

if should_generate_resume_anchor(session_store.get_recent_events(5)):
    anchor = resume_generator.generate(task, session_store.get_recent_events(5))
```

D must keep model calls off the UI thread. API/parser failure is identified by `classifier.last_error` and `result.confidence == 0.0`; it must not trigger a distraction notification.
