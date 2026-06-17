"""
Unit tests for skill-lint.py

Run with: python -m unittest tests/test_skill_lint.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import skill_lint


class TestCheckSkillMd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        (self.path / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: A test skill for unit tests. It validates behavior properly.\n---\n# Test\n",
            encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_skill(self):
        issues = skill_lint.check_skill_md(self.path)
        self.assertEqual(issues, [])

    def test_missing_name(self):
        (self.path / "SKILL.md").write_text(
            "---\ndescription: A test skill description that is valid for parsing.\n---\n",
            encoding="utf-8"
        )
        issues = skill_lint.check_skill_md(self.path)
        self.assertTrue(any("name" in msg for _, msg, _ in issues))

    def test_invalid_name(self):
        (self.path / "SKILL.md").write_text(
            "---\nname: Invalid_Name_With_Caps\ndescription: A test skill description that is valid for parsing.\n---\n",
            encoding="utf-8"
        )
        issues = skill_lint.check_skill_md(self.path)
        self.assertTrue(any("invalid name" in msg for _, msg, _ in issues))

    def test_description_too_long(self):
        long_desc = "x" * 2000
        (self.path / "SKILL.md").write_text(
            f"---\nname: test-skill\ndescription: {long_desc}\n---\n",
            encoding="utf-8"
        )
        issues = skill_lint.check_skill_md(self.path)
        self.assertTrue(any("too long" in msg for _, msg, _ in issues))

    def test_missing_skill_md(self):
        (self.path / "SKILL.md").unlink()
        issues = skill_lint.check_skill_md(self.path)
        self.assertEqual(len(issues), 1)
        self.assertIn("missing", issues[0][1].lower())


class TestCheckSecrets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_detect_github_token(self):
        (self.path / "secret.md").write_text(
            "token = 'ghp_abcdefghijklmnopqrstuvwxyz1234567890'",
            encoding="utf-8"
        )
        issues = skill_lint.check_secrets(self.path)
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any("GitHub" in msg for _, msg, _ in issues))

    def test_no_secrets(self):
        (self.path / "clean.md").write_text(
            "# Normal markdown\n\nThis is a safe file.",
            encoding="utf-8"
        )
        issues = skill_lint.check_secrets(self.path)
        self.assertEqual(issues, [])

    def test_detect_openai_key(self):
        (self.path / "secret.md").write_text(
            "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz",
            encoding="utf-8"
        )
        issues = skill_lint.check_secrets(self.path)
        self.assertTrue(any("OpenAI" in msg for _, msg, _ in issues))


class TestCheckScripts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        (self.path / "scripts").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_scripts_dir(self):
        (self.path / "scripts").rmdir()
        issues = skill_lint.check_scripts(self.path)
        self.assertEqual(len(issues), 1)
        self.assertIn("missing", issues[0][1].lower())

    def test_valid_script(self):
        (self.path / "scripts" / "test.py").write_text(
            "import sys\nimport argparse\n\ndef main():\n    p = argparse.ArgumentParser()\n    p.parse_args()\n\nif __name__ == '__main__':\n    main()\n",
            encoding="utf-8"
        )
        issues = skill_lint.check_scripts(self.path)
        # No errors expected (--help works)
        self.assertFalse(any(level == "ERROR" for level, _, _ in issues))

    def test_syntax_error(self):
        (self.path / "scripts" / "bad.py").write_text(
            "this is not valid python",
            encoding="utf-8"
        )
        issues = skill_lint.check_scripts(self.path)
        self.assertTrue(any("syntax error" in msg for _, msg, _ in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
