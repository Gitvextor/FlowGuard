# Classifier prompt v1

The versioned prompt is implemented by `app.ai.prompt_builder.build_classifier_prompt`.
It classifies one B-stage `ContextSnapshot` as `MAIN_TASK`, `NECESSARY_DETOUR`, or
`DISTRACTION`, uses task, app, title, and the attached real screenshot, requires an
exact JSON schema, treats app changes as insufficient evidence on their own, and asks
for lower confidence when the visible evidence is ambiguous.

The output schema contains exactly `state`, `confidence`, `reason`, and `task_relation`.
