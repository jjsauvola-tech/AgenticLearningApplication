import tempfile
import unittest
from pathlib import Path
from ala.build import build_id


class BuildTests(unittest.TestCase):
    def test_source_and_asset_changes_invalidate_build_but_cache_does_not(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'ala'/'__pycache__').mkdir(parents=True)
            (root/'web').mkdir()
            (root/'web'/'app.js').write_text('one')
            initial = build_id(root)  # Packaged roots may not contain main.py.
            (root/'ala'/'__pycache__'/'cache.pyc').write_bytes(b'cache')
            self.assertEqual(initial, build_id(root))
            (root/'web'/'app.js').write_text('two')
            self.assertNotEqual(initial, build_id(root))
