# ALA desktop isolation — mandatory NFR

Creating, upgrading or launching ALA must not change other applications' desktop shortcuts, icons, overlays, file associations, Explorer settings, registry preferences or icon caches.

Desktop installation may create/update ALA's own shortcut and retire an older ALA shortcut only after verifying both its target arguments and project directory. Never change global or per-user Windows shell settings as part of installation or launch. Preserve other shortcuts byte-for-byte.

A user-requested operating-system repair is a separate, explicitly scoped operation: snapshot the affected setting first, preserve shortcut files, provide rollback information, and record evidence and uncertainties. Never include such repair in ALA's normal startup path.

Record suspected breaches in docs/NFR_INCIDENTS.md. Do not claim causation or successful visual restoration without evidence.
