# Agentic Learning Application

ALA is a local learning workspace for Windows. Any course can be imported from DOCX, PDF and PPTX files. The application repository and distribution contain no course content, student records, model weights or API credentials.

Version 0.1.0 is the first working study prototype. It implements the material-import and local-storage foundation, configurable UI, notes, study cards, practice history and an optional local Ollama tutor. It is not the completed feature set of the full product specification.

The current source version is **0.2.0-dev**. It adds editable learning goals and
prerequisites, recursive course-folder import and persistent tutor source links.
See `QA_COURSE_WORKFLOW.md` for the ordered real-course verification and remaining
AI-quality and browser-download findings. This version has been tested from source on Windows;
a new packaged executable has not yet been verified.

Practice questions and feedback now require a validated structured model response
and a quotation found in the selected source. Questions display only the question;
feedback includes the quotation for checking. Invalid replies are retried once and
then rejected. See `QA_TUTOR.md` for the follow-up model checks and their limits.

## Importing a course folder

Choose **Import materials → Choose a folder (including subfolders)**, select the
course's release folder, enter a course name and press **Import materials**.
ALA recursively imports DOCX, PPTX and PDF files. Subfolder paths become
collections under the course name, preserving the module grouping. Individual
file selection is also available.

The selection preview reports supported and skipped file counts. ZIP archives,
JSON metadata, Office lock files and other unsupported files are skipped;
archives are not unpacked. A per-file report and final counts distinguish new
imports, existing content, failures and skipped files. One failed file does not
stop the remaining files. Identical content already in the active vault is not
imported again or moved to another collection.

## Learning goals and source startup

### Starting the source checkout on this Windows PC

Double-click **Start-ALA.cmd** in the project folder. It starts the local service
in the background and opens the application window. Do not open `web/index.html`
directly: the application needs its local Python service. The launcher uses the
project `.venv`, the bundled runtime available on this development PC, or an
installed Python with the required dependencies. Study data is stored in
`%LOCALAPPDATA%\ALA`. For other computers, use the packaged executable or install
the development requirements below. Exit through Settings → Exit application.

### Editing goals

Open **Learning goals / Oppimistavoitteet** in the workspace toolbar. Create a
goal, describe what you want to learn, select prerequisite goals and optionally
link the goal to the material section currently open in Study. Edit a goal to
change its self-assessed status, prerequisites or source link.

Goals cover the active vault and appear with prerequisites first. Unfinished
prerequisites, including unfinished earlier prerequisites, are highlighted.
Cycles are rejected. Status is a personal study record: it does not certify
competence or restrict access to materials. Deleting a goal removes its links
but preserves other goals and source material. Goals remain separate from
document-section progress.

Existing version 0.1 vaults are upgraded automatically. Backups include goals;
old backups can still be restored. New backups require this version or later
and cannot be restored by ALA 0.1.0. The current goal view is an ordered list
with dependency labels; a graphical node-and-edge editor remains future work.

## Running the Windows build

1. Extract the entire Windows ZIP into a folder.
2. Keep `ALA.exe` and its `_internal` folder together.
3. Start `ALA.exe`. A local workspace opens in an Edge application window, or the default browser when Edge is unavailable.
4. Import your own material and create learning vaults from Settings.

Python, Node.js, Microsoft Office and a developer environment are not required by the packaged application. Data is stored under the current Windows user's `%LOCALAPPDATA%\ALA`. Settings → Backup and restore exports the active vault to an `.ala.zip` archive. Restoring creates a separate vault and verifies original-file hashes. The source location of an imported file is not needed after import.

Exit from Settings → Exit application. The normal launcher also shuts down its local service after three minutes without browser activity. The application binds only to `127.0.0.1`, uses a random port and requires a session token for its API. The current prototype is unsigned; institution-wide deployment and signed installers remain release work.

## Available now

- Finnish and English UI, light/dark/system themes, text size and density.
- Show/hide learning-flow and assistant panels; adjust panel widths and speaker-note visibility.
- Create and switch independent SQLite learning vaults; preserve preferences across restarts.
- Import DOCX paragraphs and tables, PPTX nested groups and speaker notes, and PDF pages.
- View original PDF pages locally. DOCX and PPTX use a clearly labelled structured text view.
- Local search with source navigation, source-linked editable notes and study progress.
- Create study cards, save practice answers and self-review, revisit the original source.
- Optional Ollama chat, source context and history; generate a practice question or request formative feedback.
- Copy source context to another tool and explicitly paste an external, unverified response back.
- ZIP backup/restore and original-file download. No cloud dependency for reading, notes or stored practice.

The learning flow currently follows imported document sections. Marking a section as studied does not certify competence. The tutor cannot execute tools or change course acceptance rules.

## Local AI

Install and run Ollama separately, and download a model suitable for your computer. In Settings → Local AI, test the local connection and enter a model name returned by the service. Only a loopback HTTP endpoint is accepted. The application does not download models automatically. The local model receives the selected source excerpt and relevant text from the current vault. Speaker notes are excluded from retrieval.

The application remains useful without a model. The interface explicitly reports a missing model or connection; it does not present canned text as an AI answer. Live model quality has not been validated by the application's deterministic tests.

## Current limitations and next milestones

- Exact DOCX/PPTX layout, embedded image interpretation, animations and OCR are not implemented. Original files remain available, and import warnings identify these limitations.
- Graphical goal editing, semantic retrieval, generated mind maps, speech and web search remain planned. Goal and prerequisite editing is available in the development source.
- Cloud-provider integrations and encrypted credential storage remain planned. The current AI adapter is local Ollama only.
- Practice supports written questions, answers and feedback. Automatically scored multiple-choice tests and formal university exam administration remain planned.
- Imported files with the same name and different content coexist as distinct records; a full version-linking UI remains planned.
- The interface has keyboard focus indicators and a modal focus loop; comprehensive screen-reader and 200% zoom certification is not claimed.
- The initial local package is Windows x64. An ARM64 build is a separate target and must pass native packaging and smoke tests before being described as supported.

## Development

Python 3.12 is used for the verified Windows build. Install dependencies into an isolated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

For explicit test data placement:

```powershell
python main.py --data-dir .\data --no-browser --runtime-file .\runtime.json
```

The runtime file contains the local session URL and must not be published. Imported content is treated as data, not as executable instructions.

## Verification and packaging

```powershell
python -m unittest discover -s tests -v
python -m pip install pyinstaller==6.22.3
.\build_windows.ps1 -Python python
python tools/smoke_packaged.py dist/ALA/ALA.exe
```

Unit and HTTP tests create synthetic biology content, without depending on any particular real course. `tools/smoke_packaged.py` starts the actual EXE, imports all three formats, renders a PDF, writes notes, saves settings, exports a backup and restarts to check persistence. It uses a path containing spaces and a non-ASCII character.

See `QA_REPORT.md` for the scope of the executed checks and `PRODUCT_REQUIREMENTS.md` for the product direction.
