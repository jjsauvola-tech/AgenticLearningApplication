# NFR incidents

## 2026-09-29 — Desktop shortcut overlays

User reported shortcut arrows appearing on all desktop icons after ALA shortcut installation and requested restoration. Treat this as a reported desktop-isolation NFR breach.

Inspection found no `Shell Icons` override in HKCU or HKLM, and the normal `lnkfile/IsShortcut` marker was present. The ALA installer sets IconLocation only on its own .lnk and contains no registry or icon-cache operation. Other shortcuts retain earlier modification dates; another project's shortcut also changed around the same period. These observations do not establish the cause of the reported change. No pre-installation screenshot or registry snapshot is available.

Preventive rule: AGENTS.md now forbids changing unrelated shortcuts, shell overlays, associations, registry settings or icon caches during ALA installation, updates and launch. Any explicitly requested Windows repair must remain separate from the application.

User-authorized repair applied separately: HKCU Explorer Shell Icons value 29 now points to a transparent overlay. Previous setting and a rollback `.reg` were saved under `%LOCALAPPDATA%\ALA-Desktop-Restore\20260929-135650`. SHA-256 verification confirmed all 26 desktop shortcut files unchanged. The shell refresh was requested, but visual disappearance of the overlay was not independently verified. This repair script is not part of ALA installation or startup.

## 2026-09-29 — Open windows disconnected during updates

Previous launcher versions changed the port and session token after restart. Open browser windows could then show connection errors for both AI and notes. Version 0.2.3 reuses the previous local endpoint and token, and the crash-recovery test verifies URL equality. A busy port can still require a new endpoint; reopening through the desktop launcher gives the current one.

Note drafts now persist in browser local storage before submission and across reloads. Retries reuse the note ID, and writes retain the originating vault. An explicit failure message stays in the note dialog; a failed write is never reported as saved.
