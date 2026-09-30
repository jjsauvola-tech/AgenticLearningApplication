# ALA 0.2.4-dev handoff — 2026-09-30

## Base and scope
Continues main commit 24ad5fb from the other computer (0.2.3-dev).
The earlier codex/v0.2-learning-quiz-handoff branch remains separate: do not merge
its alternative schema wholesale. No real course materials or student data are
included in the source repository or distribution.

## Implemented
- Source-anchored research-question practice: original attempt → clarification →
  revision → independent application → reflection → saved summary.
- Finnish and English UI, progressive fixed hints, original-answer preservation,
  source snapshot, support-event history and return to supported practice.
- SQLite schema 3, pre-migration database backup, vault-scoped records, transactional
  idempotent requests and revision conflicts protecting concurrent edits.
- Browser draft recovery and retries; independent application hides this practice's
  source and hints. It does not prevent access to other apps or materials.

## Verification
- 63 Python tests passed, including concurrent duplicate requests, vault isolation,
  migration/backup/restart, HTTP authentication and stale revision rejection.
- 23 JavaScript tests passed, including production script load order and blocked
  browser-storage fallback. A browser-discovered global function scope bug was
  fixed and covered by the production-load regression test.
- Rebuilt Windows x64 executable passed synthetic DOCX/PDF/PPTX imports, PDF
  rendering, notes/settings persistence, inquiry retry/restart and backup smoke.
- Browser walkthrough completed all five answer phases, requested a hint, reloaded
  a draft during independent application and visually inspected the saved summary.
- CI now runs JavaScript tests as well as Python and executable checks on Windows
  x64/ARM64. Check the workflow run for this commit for hosted results.

## Continue on another computer
Pull main, then use Start-ALA.cmd (source setup) or the Windows CI artifact.
Transfer personal data using the application's backup/restore; Git contains no
personal vault. Close the old instance before launching a newer executable.
Existing schema 1/2 databases migrate to 3 with a .before-v3.bak snapshot. Do not
open the upgraded database with an older app; keep a full exported backup too.

## Next work and limits
This is the first Phase B foundation from UX_PEDAGOGY_SPEC.md, not its complete
adaptive teaching controller. Next: source-validated adaptive feedback, explicit
rubrics and more task types. Current fixed prompts do not grade answer quality.
Unsent drafts belong to this browser; use Save and continue before transferring
machines. Drafts from a stale phase remain locally stored but are not shown in the
new phase after another window advances it. No new live-model quality claim was
made. Course imports must contain extractable text; scanned documents need OCR.
Desktop shortcuts and Windows shell settings were not modified by this update.
