# Ordered course workflow verification — 28 September 2026

Source version: 0.2.0-dev. The user's external release folder was used as input.
No course files or generated study content are committed to the application.

## Results in execution order

| Step | Check | Result |
|---|---|---|
| 1 | Browser folder picker, recursive import and module grouping | 42 imported: 33 DOCX and 9 PPTX, zero failures. 21 JSON files and one ZIP skipped. 12 folder collections retained. |
| 2 | Every imported original, section and PowerPoint slide | 824 sections total, including 222 PPTX slides. All original SHA-256 hashes matched. All 222 speaker-note fields matched their source slides. |
| 3 | Repeat import of all supported files | All 42 recognized as duplicates; no extra documents. |
| 4 | Material display, navigation, course filtering and search | DOCX and PPTX opened in browser; slide navigation and search source links worked. Cross-module navigation defect fixed. |
| 5 | Notes and study progress | Browser note creation/editing, source return and studied status passed. API tested all progress states and restart persistence. |
| 6 | Study cards, attempts and external answers | Browser card creation/answer reveal, written practice save and unverified external-answer label passed. Stored records checked through API. |
| 7 | Goals and prerequisites | Browser source-linked goals, dependency display and completed prerequisite passed. API checked cycle rejection, deletion and isolation. |
| 8 | Settings | Finnish/English, dark theme, font size, density, reduced motion, panel visibility, alternate material selector, speaker notes and reset exercised in browser. All persisted settings, including panel widths, checked through API and restart. |
| 9 | Vaults, backup and restore | Full corpus and study records round-tripped through backup. Every restored original matched its hash. Empty vault isolation and switching passed. Browser restored the backup into a new test vault; 42 documents, the note and card were verified. |
| 10 | Model connection and errors | Model discovery, unconfigured/unavailable services and empty-answer handling covered. Deterministic adapter test covers source context without asserting AI quality. |
| 11 | Live local model | llama3.2:1b and qwen3.5:9b exercised with this course. Explanation, question generation and feedback returned through the real Ollama service. Browser chat, question generation, feedback and source navigation also exercised. See quality findings below. |
| 12 | Conversation sources and restart | Source buttons survive reload; source metadata also survives restart and backup/restore. |
| 13 | PDF and shutdown | Release contains no PDF. Synthetic PDF import/rendering passed separately. Clean shutdown and restart passed. |

Final automated results: **25 Python tests, 3 JavaScript import-planning tests,
and all 13 ordered integration checkpoints passed**. This describes functional
checks, not an assertion that every possible interaction or model answer is correct.

## Defects corrected during the run

- Added whole-folder import with subfolder collections, selection counts,
  per-file results, duplicate counts, skipped files and continued processing
  after an individual file error.
- Fixed a function-local urllib import that caused model discovery to return 500.
- Fixed backup export when the caller relies on the active vault rather than
  supplying a vault ID explicitly.
- Updated the course filter when a source link opens another module.
- Persisted answer source links instead of losing them on reload.
- Disabled optional model thinking output for direct tutor responses and reject
  empty answers explicitly instead of recording them as successful replies.
- Kept question generation and feedback on the selected source section; unrelated
  conversation history and query-dependent extra retrieval no longer change the
  practice source context.

## Remaining findings and boundaries

- **AI teaching quality is not accepted as complete.** The small model produced
  weak Finnish and disclosed an answer. The larger model was clearer, but also
  produced factual/terminological inaccuracies. In the final sample its question
  included a source explanation that effectively revealed the answer. Functional
  success must not be read as pedagogical reliability or grading validity.
- Original-file and backup HTTP downloads were validated byte-for-byte or by
  successful restore. The in-app browser's download event did not arrive in two
  original-file UI attempts, so **desktop save completion remains unverified**.
  No success is claimed for that browser download event.
- Exact PowerPoint/Word appearance, pictures, OCR and animations are not part of
  the current structured-text reader. No new EXE build or ARM64 certification.
- Browser test records are isolated in named test vaults. The user's original
  vault retains the imported course, and original settings and active vault were
  restored after testing. Original Dropbox files were not changed.

## Reproduction

```powershell
python -m unittest discover -s tests -v
node --test tests/test_import_plan.cjs
python tools/verify_course.py PATH_TO_RELEASE --report data/course-check.json
# Optional installed local model; nothing is sent to a cloud service:
python tools/verify_course.py PATH_TO_RELEASE --report data/course-check-live.json --live-model qwen3.5:9b
```

The ordered runner creates temporary isolated study data and cleans it up.
Reports with real course answers stay under the ignored `data` directory.
