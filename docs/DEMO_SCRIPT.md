# FlowGuard fixed demo script

## Preparation

1. Use Windows notification settings to allow notifications from FlowGuard.
2. In PowerShell, run `$env:FLOWGUARD_MOCK="true"` and then `python main.py`.
3. Enter `完成操作系统 Priority Scheduling 实验` and click **开始护航**.
4. Keep every target window stable for at least two seconds. Screenshots stay in memory.

## Two-minute path

1. Open VS Code with `process_scheduling.c` visible. Confirm `MAIN TASK` and a green status.
2. Open Edge with a page titled `priority scheduling implementation` or Stack Overflow. Confirm `NECESSARY DETOUR`, amber status, and no notification.
3. Open a Bilibili entertainment page. Confirm `DISTRACTION`, red status, and one Windows notification.
4. Move between two clearly unrelated entertainment titles to create the second confirmed distraction. Confirm the Resume Anchor is evidence-bounded.
5. Return to VS Code. Confirm monitoring continues and the timeline contains no screenshots.
6. Click **暂停**. Switch windows and confirm no new timeline entry appears.

## Backup recording checklist

Record a 1–2 minute MP4 showing the exact path above. Capture both the FlowGuard window and Windows notification area. Also record the terminal outputs of `python evaluation/run_eval.py` and the packaged `dist/FlowGuard/FlowGuard.exe` starting. Store the video outside Git or in the team's agreed large-file storage, then add its location to `HANDOFF_FINAL.md`.

Do not claim the recording exists until a human has opened and watched the final file with audio/video playback verified.
