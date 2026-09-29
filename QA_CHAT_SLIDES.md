# Chat and slide preview verification — 2026-09-28

- Fixed shared `.assistant` CSS selector assigning panel dimensions to response bubbles.
- Added expand/restore, width control, vertical panel resize, and resizable full-answer dialog.
- Added answer copy and note-save actions, preserving source references and captured vault.
- Added static PowerPoint slide preview in the center reader with Show slide / Show text controls. Images are cached per original content hash and slide number. Source decks are opened read-only, macros disabled during export.
- 33 Python regression tests passed; 5 JavaScript tests passed, including full long-answer copy and vault/source-safe note saving.
- Real release Module 01 slides 1 and 2 rendered at 1600x900; slide 2 visually inspected. Preview HTTP returned 200 and a 105577-byte PNG.
- End-to-end browser checks of resizing and clipboard buttons remain unverified: browser control stalled for approximately 28 minutes. Unit-level clipboard and note-save behavior passed; these are not a substitute for visual browser verification.
- Requires Windows and installed PowerPoint; animations are not played. Other platforms retain text view and original download.

The later browser checks and stability work are recorded in QA_ROBUSTNESS.md. The earlier browser-verification gap above has now been partly closed: long answer display, exact clipboard copy, note persistence, responsive chat and real PPTX display were checked on 2026-09-29.
