# ALA 0.2.0-dev — Windows continuation, 28 September 2026

Baseline: GitHub main commit `a3820e9ebca32cbebbca60f8cd51b308400518ca`.
The user confirmed Dropbox had finished syncing before the repository was cloned
into this machine's local project workspace.

## Executed checks

- Baseline: all 12 existing Python unit and HTTP tests passed.
- Updated suite: all 21 tests passed, including nine new goal tests.
- New coverage: prerequisite ordering and transitive readiness, cycle rejection
  without partial writes, vault isolation, deletion of dependency links, source
  anchors, restart persistence, backup round trip, v1 database migration, v1
  backup restore, invalid input, HTTP lifecycle and authentication.
- JavaScript syntax checks passed for `web/app.js` and `web/goals.js`.
- Browser: created two synthetic biology goals, linked the second to the first,
  observed the unfinished prerequisite, changed the first to studied and
  observed the second become ready. The goal dialog was visually inspected at
  the browser's narrow viewport.

The tests ran using the bundled local Python runtime and its installed packages,
not a freshly installed environment matching every pinned requirement.

## Release boundaries

No new EXE packaging or packaged smoke test was run in this continuation.
PyInstaller is not installed in the available runtime. No ARM64, live tutor,
screen-reader or broad accessibility certification is claimed. Version 0.1
packaging evidence remains in `QA_REPORT.md` and must not be attributed to 0.2.

Goal dependencies are presented as an ordered list with prerequisite labels.
A graphical node editor is not implemented. Goal status is self-assessment;
it does not certify competence or prevent reading material out of order.

Database schema is now 2. Schema 1 vaults migrate automatically and schema 1
backups are accepted. Exported schema 2 backups require the updated application.

## Windows launcher correction

Added Start-ALA.cmd and scripts/start.ps1 after direct file opening produced a blank page. Verified the launcher with an isolated data directory and then launched the normal local application. Its authenticated state endpoint responded, and the Study interface was observed in the browser. All 21 tests passed again. Direct HTML opening now displays startup instructions. No EXE packaging is claimed.
