"""
Unit tests for _common.py

Run with: python -m unittest tests.test_common
Or:       python -m unittest discover tests
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts/ to path so we can import _common
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import _common


class TestVaultPath(unittest.TestCase):
    def test_basic_path(self):
        v = _common.VaultPath("/tmp/test_vault")
        self.assertEqual(v.root, Path("/tmp/test_vault"))

    def test_global_file(self):
        v = _common.VaultPath("/tmp/test_vault")
        self.assertEqual(
            v.global_file("00-profile.md"),
            Path("/tmp/test_vault/_global/00-profile.md")
        )

    def test_platform_dir(self):
        v = _common.VaultPath("/tmp/test_vault")
        # CN alias → 国内
        self.assertEqual(
            v.platform_dir("CN", "xiaohongshu"),
            Path("/tmp/test_vault/国内/xiaohongshu")
        )
        self.assertEqual(
            v.platform_dir("国内", "xiaohongshu"),
            Path("/tmp/test_vault/国内/xiaohongshu")
        )

    def test_cards_dir(self):
        v = _common.VaultPath("/tmp/test_vault")
        self.assertEqual(
            v.cards_dir("INTL", "youtube", "W1-起号期"),
            Path("/tmp/test_vault/国外/youtube/04-内容卡/W1-起号期")
        )

    def test_cards_dir_no_week(self):
        v = _common.VaultPath("/tmp/test_vault")
        self.assertEqual(
            v.cards_dir("CN", "douyin"),
            Path("/tmp/test_vault/国内/douyin/04-内容卡")
        )

    def test_special_paths(self):
        v = _common.VaultPath("/tmp/test_vault")
        self.assertEqual(v.profile(), Path("/tmp/test_vault/_global/00-profile.md"))
        self.assertEqual(v.inspirations(), Path("/tmp/test_vault/_global/06-inspiration.md"))
        self.assertEqual(v.failures(), Path("/tmp/test_vault/_global/07-failures.md"))
        self.assertEqual(v.cross_platform_compare(), Path("/tmp/test_vault/_global/05-跨平台对比.md"))


class TestLoadConfig(unittest.TestCase):
    def test_none_path(self):
        self.assertEqual(_common.load_config(None), {})

    def test_empty_path(self):
        self.assertEqual(_common.load_config(Path("")), {})
        self.assertEqual(_common.load_config(Path(".")), {})

    def test_nonexistent_path(self):
        self.assertEqual(_common.load_config(Path("/nonexistent/file")), {})

    def test_valid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.md"
            target.write_text("---\nkey: value\nnumber: 42\n---\n", encoding="utf-8")
            config = _common.load_config(target)
            self.assertEqual(config.get("key"), "value")
            self.assertEqual(config.get("number"), 42)

    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.md"
            target.write_text("---\ninvalid: yaml: with: too: many: colons\n---\n", encoding="utf-8")
            config = _common.load_config(target)
            self.assertEqual(config, {})


class TestParseFrontmatter(unittest.TestCase):
    def test_no_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "test.md"
            target.write_text("# Just a heading\n\nSome content.", encoding="utf-8")
            meta = _common.parse_frontmatter(target)
            self.assertEqual(meta, {})

    def test_valid_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "test.md"
            target.write_text("---\ntitle: Test\ncount: 5\n---\n# Body\n", encoding="utf-8")
            meta = _common.parse_frontmatter(target)
            self.assertEqual(meta.get("title"), "Test")
            self.assertEqual(meta.get("count"), 5)

    def test_nonexistent_file(self):
        meta = _common.parse_frontmatter(Path("/nonexistent/file.md"))
        self.assertEqual(meta, {})

    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "test.md"
            target.write_text("---\nbad: yaml: here: too: many:\n---\n", encoding="utf-8")
            meta = _common.parse_frontmatter(target)
            self.assertEqual(meta, {})


class TestFormatTable(unittest.TestCase):
    def test_basic(self):
        result = _common.format_table(["A", "B"], [["1", "2"], ["3", "4"]])
        self.assertIn("| A", result)
        self.assertIn("| 1", result)
        self.assertIn("| 3", result)

    def test_truncation(self):
        long = "x" * 100
        result = _common.format_table(["col"], [[long]], max_col_width=10)
        self.assertIn("…", result)

    def test_empty(self):
        result = _common.format_table([], [])
        self.assertIn("|", result)


class TestSafeWrite(unittest.TestCase):
    def test_write_new(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sub" / "file.md"
            result = _common.safe_write(target, "hello")
            self.assertTrue(result)
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "hello")

    def test_skip_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "file.md"
            target.write_text("original", encoding="utf-8")
            result = _common.safe_write(target, "new content", overwrite=False)
            self.assertFalse(result)
            self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "file.md"
            target.write_text("original", encoding="utf-8")
            result = _common.safe_write(target, "new content", overwrite=True)
            self.assertTrue(result)
            self.assertEqual(target.read_text(encoding="utf-8"), "new content")


class TestSetupLogging(unittest.TestCase):
    def test_returns_logger(self):
        import logging
        logger = _common.setup_logging(verbose=False)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "creator-incubator")

    def test_verbose_includes_debug(self):
        import logging
        logger = _common.setup_logging(verbose=True)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_idempotent(self):
        logger1 = _common.setup_logging()
        handlers1 = len(logger1.handlers)
        logger2 = _common.setup_logging()
        handlers2 = len(logger2.handlers)
        self.assertEqual(handlers1, handlers2)


class TestHandleErrors(unittest.TestCase):
    def test_successful_call(self):
        @_common.handle_errors
        def returns_zero():
            return 0
        self.assertEqual(returns_zero(), 0)

    def test_keyboard_interrupt(self):
        @_common.handle_errors
        def raises_kb():
            raise KeyboardInterrupt()
        result = raises_kb()
        self.assertEqual(result, 130)

    def test_file_not_found(self):
        @_common.handle_errors
        def raises_fnf():
            raise FileNotFoundError("test.txt")
        result = raises_fnf()
        self.assertEqual(result, 2)

    def test_yaml_error(self):
        @_common.handle_errors
        def raises_yaml():
            import yaml
            raise yaml.YAMLError("bad yaml")
        result = raises_yaml()
        self.assertEqual(result, 4)

    def test_generic_exception(self):
        @_common.handle_errors
        def raises_generic():
            raise ValueError("oops")
        result = raises_generic()
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
