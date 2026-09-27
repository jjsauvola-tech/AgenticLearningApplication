# ALA product requirements

ALA is a Windows 11 learning application for arbitrary user-imported courses. The application source, release binaries and automated unit tests must remain independent of any example course. Real course corpora are external test inputs and are never committed to this repository.

## Accepted settings requirements

- Students choose the UI language from Settings. Finnish and English are the first implemented languages; the source content is not silently translated.
- Students adjust theme, font size, density, pane visibility, pane width and speaker-note visibility.
- Preferences are persisted locally and can be reset without deleting study data.
- Students create and switch independent learning databases/vaults.
- A vault contains imported originals, extracted content, notes, conversations, cards, attempts and progress.
- Vaults can be backed up and restored on another Windows account without the original source paths.

## Learning experience

Three primary views cover Study, AI teacher and Learning verification. Study combines a learning flow, a material reader and a context-aware assistant. The target flow supports editable goals and prerequisites; version 0.1 follows document sections. The teacher view supports notes, practice and cards, with mind maps, visualizations and speech planned. Verification distinguishes formative practice from official institutional assessment.

DOCX, PDF and PPTX import must preserve originals and source anchors. Grouped PowerPoint shapes and separate speaker notes must be handled. Failures, encrypted documents, duplicates, missing text and unsupported visual interpretation must be explained. Source-grounded answers must link back to material. Content instructions must never grant tool permissions.

Offline reading and local study records must work without a model. Local and cloud AI are product targets; the first adapter uses local Ollama. No silent fallback from local processing to a cloud service is allowed. External answers pasted by the student are labelled unverified.

## Deployment goals

The student-facing package must not require Office, Python, Node.js, Git, Dropbox, Codex, Docker or a discrete GPU. x64 and ARM64 are separate verification targets. The fact that a program runs on one developer machine does not establish compatibility on all Windows devices. Institution-managed installation restrictions, code signing, accessibility, update recovery and hardware capacity must be addressed before a general release.

## Validation

Each release records what was actually tested. Core checks include all three formats, nested PPTX groups, malformed/encrypted documents, vault isolation, persistence after restart, backup recovery, source navigation, language switching, UI customization and handling of missing AI services. Live tutor quality, official grading validity and OCR quality require additional evaluation and cannot be inferred from parser tests.
