# Verification record for ALA

## Version 0.2.0 handoff, 28 September 2026

18 local unit/HTTP tests passed, including dependency-cycle rejection, cross-course validation, vault isolation, immutable quiz scoring, repeated submission, card editing, new-record backups and version-1 database migration. Both JavaScript syntax checks passed. The packaged Windows x64 EXE smoke test passed imports, PDF rendering, settings, notes, goals, quiz scoring, card editing, backup and restart persistence. Browser testing verified creation and display of a source-linked goal; remaining UI checks and desktop shortcut installation are explicitly listed in `HANDOFF.md`. Check the new GitHub Actions run for this version's x64/ARM64 result.

## Version 0.1.0 baseline

Prepared during the first Windows implementation, 27–28 September 2026.

## Executed checks

| Check | Observed result |
|---|---|
| Python unit and HTTP integration suite | 12 tests passed |
| JavaScript syntax check | Passed |
| Synthetic DOCX | Paragraph and table content imported |
| Synthetic PPTX | Nested groups extracted; speaker notes kept outside retrieval text |
| Synthetic PDF | Blank/image-only text condition flagged as requiring OCR |
| Malformed and encrypted input | Rejected |
| Duplicate and updated material | Duplicate identified; distinct version preserves prior note anchor |
| Independent vaults | Documents isolated; settings and active vault survive a new Store instance |
| Backup restored to another directory | Source hashes and notes preserved |
| Malicious ZIP traversal | Rejected |
| Unauthenticated and cross-origin API requests | Rejected |
| Missing local model | Explicit configuration error; no fabricated answer |
| Packaged Windows x64 executable | Startup, all three imports, PDF PNG rendering, note, settings, backup and restart persistence passed |
| Unicode and space-containing data path | Passed in packaged-executable smoke test |
| External course corpus | 51 imports passed: 33 DOCX, 9 PPTX, 9 PDF; 0 errors; source slide/page counts matched |

The full external corpus importer run took 7.72 seconds on this machine. This is a single local observation, not a portable performance guarantee. The corpus is not stored in this repository or bundled with the application.

## Browser observations

The running local interface was exercised through the browser: settings were opened; the language changed from Finnish to English and back; dark and light themes were selected; a second vault was created; DOCX, PPTX and PDF files were imported through the file picker; a source-linked note was saved; an original PDF page was displayed; the assistant panel was hidden; and a page reload preserved settings and the note. A practice answer and self-review were saved, a study card was created and its answer revealed, and switching to the original empty vault confirmed that the other vault's materials and notes were absent.

The checks verify the operations described, not complete accessibility certification. No screen-reader, physical ARM64-device or broad fleet test has yet been recorded here. Continuous-integration Windows x64 and ARM64 packaging jobs are supplied, and their outcomes must be checked separately.

## Boundaries

No live language-model quality evaluation or paid model request was performed. Formative practice is not institutional assessment. OCR, exact Office rendering, goal graphs, cloud adapters, speech and mind maps are future work. The executable is unsigned. No claim is made that the complete product specification has been implemented.

## Reproduction

Run `python -m unittest discover -s tests -v`, package with `build_windows.ps1`, and run `python tools/smoke_packaged.py dist/ALA/ALA.exe`. Tests synthesize generic materials; a real course corpus is optional external evidence. Data directories and session URLs must remain outside version control.
