"""Identify the actual local source snapshot, including uncommitted changes."""
import hashlib
from pathlib import Path
from . import __version__


def build_id(root='.'):
    root = Path(root)
    paths = [root / 'main.py']
    paths += list((root / 'ala').rglob('*.py'))
    paths += [p for p in (root / 'web').rglob('*') if p.is_file()]
    digest = hashlib.sha256(__version__.encode())
    for path in sorted(p for p in paths if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
    return digest.hexdigest()[:10]
