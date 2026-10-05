# Resume prompt v1

The versioned evidence constraints are implemented by
`app.ai.prompt_builder.build_resume_anchor_prompt` for integrations that can provide
text-only requests. The stable A-stage `LLMClient.analyze(image, prompt, context)` is
vision-only, while the shared `ResumeAnchorGenerator.generate(task, history)` contract
does not provide a screenshot. To avoid fabricating or substituting an image, the
current generator deterministically constructs a conservative anchor from the last
five `HistoryEvent` records. The exact unresolved problem is reported as unclear unless
future shared evidence explicitly records it.

The required output fields are `last_position`, `current_problem`, and `next_step`.
