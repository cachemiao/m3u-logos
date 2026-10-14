"""Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from catalog import collect
from build import build
from import_folder import import_folders


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("tv", "radio", "data"):
            (self.root / name).mkdir()
        self.write([])

    def write(self, entries):
        (self.root / "data/channels.json").write_text(json.dumps(entries), "utf-8")

    def add(self, id="one", file="One.png", alias="ONE", size=(300, 180)):
        Image.new("RGBA", size, (255, 0, 0, 128)).save(self.root / "tv" / file)
        return {"id": id, "name": id, "file": file, "category": "tv", "aliases": [alias],
                "source": "test fixture", "usage": "test only"}

    def test_empty_build(self):
        build(self.root)
        index = json.loads((self.root / "data/logos.json").read_text())
        self.assertEqual(index["total"], 0)

    def test_valid_build_and_aliases(self):
        self.write([self.add(alias=" ＯＮＥ ")])
        build(self.root)
        self.assertTrue((self.root / "dist/tv/One.png").exists())
        aliases = json.loads((self.root / "data/aliases.json").read_text())
        self.assertEqual(aliases["aliases"]["tv"]["one"], "one")

    def test_alias_conflict(self):
        self.write([self.add(), self.add("two", "Two.png", "one")])
        self.assertTrue(collect(self.root)[1])

    def test_invalid_dimensions(self):
        self.write([self.add(size=(100, 100))])
        self.assertTrue(collect(self.root)[1])

    def test_corrupt_file_does_not_replace_build(self):
        self.write([self.add()])
        build(self.root)
        index = (self.root / "dist/api/v1/logos.json").read_bytes()
        (self.root / "tv/One.png").write_bytes(b"not a PNG")
        with self.assertRaises(ValueError):
            build(self.root)
        self.assertEqual((self.root / "dist/api/v1/logos.json").read_bytes(), index)

    def test_unregistered_file(self):
        self.add()
        self.assertTrue(collect(self.root)[1])

    def test_traversal(self):
        entry = self.add()
        entry["file"] = "../One.png"
        self.write([entry])
        self.assertTrue(collect(self.root)[1])

    def test_nontransparent_is_notice(self):
        entry = self.add()
        Image.new("RGB", (300, 180), "red").save(self.root / "tv/One.png")
        self.write([entry])
        _, errors, notices = collect(self.root)
        self.assertFalse(errors)
        self.assertTrue(notices)

    def test_import_and_reject_overwrite(self):
        shutil.copytree(Path(__file__).resolve().parents[1] / "scripts", self.root / "scripts")
        source = self.root / "fixture.png"
        Image.new("RGBA", (300, 180), (0, 255, 0, 128)).save(source)
        command = [sys.executable, str(self.root / "scripts/import.py"), str(source),
                   "--id", "one", "--name", "One", "--category", "tv", "--file", "One.png",
                   "--source", "test fixture", "--usage", "test only"]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = (self.root / "data/channels.json").read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual((self.root / "data/channels.json").read_bytes(), before)
        self.assertEqual(len(collect(self.root)[0]), 1)

    def test_batch_dry_run_and_import(self):
        folder = self.root / 'source'
        folder.mkdir()
        Image.new('RGBA', (300, 180), (0, 0, 255, 128)).save(folder / '电视台.png')
        Image.new('RGB', (50, 50)).save(folder / 'Wrong.png')
        (folder / 'Thumbs.db').write_bytes(b'cache')
        report_path = self.root / 'report.json'
        report = import_folders({'tv': folder}, 'fixture', 'test only', report_path, root=self.root)
        self.assertEqual(report['counts']['tv'], 1)
        self.assertEqual(len(report['skipped']), 2)
        self.assertFalse((self.root / 'tv/电视台.png').exists())
        import_folders({'tv': folder}, 'fixture', 'test only', report_path, apply=True, root=self.root)
        self.assertTrue((self.root / 'tv/电视台.png').exists())
        repeat = import_folders({'tv': folder}, 'fixture', 'test only', report_path, apply=True, root=self.root)
        self.assertEqual(repeat['counts']['tv'], 0)
        self.assertEqual(len(collect(self.root)[0]), 1)


if __name__ == "__main__":
    unittest.main()
