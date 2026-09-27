# Agentic Learning Application

ALA is a local learning workspace for Windows. Any course can be imported from DOCX, PDF and PPTX files. The application repository and distribution contain no course content, student records, model weights or API credentials.

Version 0.1.0 is the first working study prototype. It implements the material-import and local-storage foundation, configurable UI, notes, study cards, practice history and an optional local Ollama tutor. It is not the completed feature set of the full product specification.

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
- The editable learning-goal dependency graph, semantic retrieval, generated mind maps, speech and web search remain planned.
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