import tempfile
import unittest
from pathlib import Path

from scripts.sync_skills import inject_token, synchronize


class SyncSkillsTests(unittest.TestCase):
    def test_copy_update_delete_and_preserve_non_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source"
            target = base / "target"
            (source / "domain" / "base").mkdir(parents=True)
            (target / "domain" / "base").mkdir(parents=True)
            (target / "old").mkdir(parents=True)

            (source / "domain" / "base" / "new.md").write_text("new", encoding="utf-8")
            (source / "domain" / "base" / "changed.md").write_text("new value", encoding="utf-8")
            (target / "domain" / "base" / "changed.md").write_text("old value", encoding="utf-8")
            (target / "old" / "removed.md").write_text("remove", encoding="utf-8")
            (target / "keep.yml").write_text("keep", encoding="utf-8")

            result = synchronize(source, target, delete=True, dry_run=False)

            self.assertEqual((target / "domain" / "base" / "new.md").read_text(), "new")
            self.assertEqual((target / "domain" / "base" / "changed.md").read_text(), "new value")
            self.assertFalse((target / "old" / "removed.md").exists())
            self.assertTrue((target / "keep.yml").exists())
            self.assertIn("domain/base/new.md", result["copied"])
            self.assertIn("domain/base/changed.md", result["updated"])
            self.assertIn("old/removed.md", result["deleted"])

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()
            (source / "skill.md").write_text("source", encoding="utf-8")

            result = synchronize(source, target, delete=True, dry_run=True)

            self.assertFalse((target / "skill.md").exists())
            self.assertIn("skill.md", result["copied"])

    def test_inject_token_encodes_credentials(self):
        value = inject_token("https://gitlab.example/group/project.git", "a:b@c", "oauth2")
        self.assertEqual(value, "https://oauth2:a%3Ab%40c@gitlab.example/group/project.git")


if __name__ == "__main__":
    unittest.main()
