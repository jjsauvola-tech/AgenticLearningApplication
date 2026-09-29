# ALA stability verification — 2026-09-29

Status: critical stability fixes implemented and tested. New product features remain frozen. This is not a declaration of production readiness.

## Implemented

- OS-level exclusive ownership of each data directory; concurrent launches reuse the existing service. Reacquire after a shutting-down owner exits. PowerShell launcher accepts successful reuse even when its child exits.
- Per-port session cookies; a request captures its vault before asynchronous work. Background tabs no longer trigger an idle shutdown.
- Snapshot web assets for a consistent running build; explicit restart loads new source.
- Optional data loads fail independently. Failed bootstrap displays retry controls. Interface faults persist until successful recovery. Network calls have deadlines and writes are not blindly retried.
- Chat drafts survive page reload in the same origin/session. Stale document and whole-workspace responses cannot replace newer selections. Practice responses are guarded against changed context.
- Rotating local diagnostics with event identifiers and sanitized stack locations, without document contents or tokens.
- At most 16 request handlers and 2 expensive requests. Saturation returns a busy response while ordinary requests can continue.
- Isolated, disposable processes with deadlines for imports and PDF/PPTX rendering. Parser/renderer failures do not terminate the API service.
- Fsynced atomic configuration writes and in-memory rollback on failed configuration persistence. Slide cache writes use atomic replacement.

## Automated evidence

- Python suite: 46 tests passed (including inherited HTTP regressions).
- JavaScript suite: 12 tests passed.
- Ten simultaneous CLI launches: one owner. The PowerShell launcher also reuses that owner. Forced owner termination releases the lock and permits recovery.
- Injected optional-load failure, delayed workspace/document responses, request timeout, disk-write failure, saturated expensive-job slots, worker timeout, malformed input, competing-vault switch, and diagnostic privacy tests passed.
- Windows test harness normalizes inherited environment variable keys when invoking PowerShell to avoid duplicate Path/PATH entries supplied by the test environment.

## Real release corpus

All tests use an isolated temporary vault. Original Dropbox files were not changed.

| Run | Files | Concurrent HTTP clients | Requests | p95 | Max | Notes restored |
|---|---:|---:|---:|---:|---:|---:|
| 60 seconds | 42 | 4 | 8,626 | 31 ms | 78 ms | 1,727 |
| 300 seconds | 42 | 4 | 41,035 | 31 ms | 109 ms | 8,209 |

These runs imported all DOCX/PPTX/PDF inputs through the production HTTP import path, mixed document reads and note writes, exported/restored the database and originals, and verified unchanged input hashes. The load phase did not benchmark LLM generation or PowerPoint rendering. Detailed local output is in ignored data/robustness-report.json and data/robustness-300s-report.json.

## Browser evidence

- Workspace opens with the imported 42-document corpus; original user vault restored after testing.
- Full-answer dialog displays a 13,000-character response. Clipboard text exactly matches the whole response including its final marker.
- Save-to-notes was clicked in the QA vault; HTTP readback confirms an exact 13,000-character match.
- A chat draft survived conversation expansion and page reload.
- PPTX slide image, slide/text controls and next-slide navigation worked.
- Responsive checks at 390 x 844: material layout and expanded chat remained usable; viewport override reset afterwards.
- Final restarted build visibly opened the workspace; screenshot saved locally as data/robustness-ui.png.
- Browser automation intermittently stalled far beyond its requested timeout. This is a verification-tool limitation; it does not establish the cause of the user's original generic error, which was not reproduced with diagnostics.

## Remaining release gates

The original ten-point architecture list is not fully closed. In particular:

- Eight-hour endurance and operating-system sleep/wake tests have not been run. Five minutes is not evidence of all-day reliability.
- Clean-machine Windows x64/ARM64 packaging and rollback verification remain open. PowerPoint is still a dependency for visual PPTX previews; the reader has a text fallback.
- Large-library pagination, full data/backup disk-full and interruption matrices, native PowerPoint orphan-process behavior, and job cancellation require further hardening.
- Document work is isolated; LLM calls retain a bounded synchronous request path. There is no durable job queue.
- Draft recovery currently covers chat within the same browser origin/session, not every form across a changed service port.

Do not start new product features while these release gates are being addressed. Do not label this source revision a fully robust release based only on unit counts or the short HTTP benchmark.
