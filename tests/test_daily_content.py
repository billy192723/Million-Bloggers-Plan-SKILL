"""
Unit tests for daily-content.py and failure-manager.py

Run with: python -m unittest tests.test_daily_content
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import date

# Add scripts/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import daily_content
import failure_manager


class TestFindActivePlatforms(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)
        (self.vault / "_global").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_profile_returns_douyin_default(self):
        platforms = daily_content.find_active_platforms(self.vault)
        self.assertEqual(platforms, [("CN", "抖音")])

    def test_with_active_platforms(self):
        profile = self.vault / "_global" / "00-profile.md"
        profile.write_text(
            "---\ntype: user-profile\ntarget_platforms: [['CN', '小红书'], ['INTL', 'YouTube']]\n---\n",
            encoding="utf-8"
        )
        platforms = daily_content.find_active_platforms(self.vault)
        self.assertIn(("CN", "小红书"), platforms)
        self.assertIn(("INTL", "YouTube"), platforms)

    def test_fallback_checkbox_parsing(self):
        profile = self.vault / "_global" / "00-profile.md"
        profile.write_text(
            "---\ntype: user-profile\n---\n# Profile\n- [x] 抖音\n- [x] B站\n- [ ] 公众号\n",
            encoding="utf-8"
        )
        platforms = daily_content.find_active_platforms(self.vault)
        plat_names = [p for _, p in platforms]
        self.assertIn("抖音", plat_names)
        self.assertIn("B站", plat_names)
        self.assertNotIn("公众号", plat_names)


class TestFindUpcomingHolidays(unittest.TestCase):
    def test_within_7_days(self):
        v = Path("/tmp")
        holidays = daily_content.find_upcoming_holidays(v, days_ahead=7)
        self.assertIsInstance(holidays, list)
        for h in holidays:
            self.assertIn("date", h)
            self.assertIn("days_until", h)
            self.assertIn("name", h)
            self.assertIn("themes", h)
            self.assertGreaterEqual(h["days_until"], 0)
            self.assertLessEqual(h["days_until"], 7)

    def test_no_negative_days(self):
        v = Path("/tmp")
        holidays = daily_content.find_upcoming_holidays(v, days_ahead=7)
        for h in holidays:
            self.assertGreaterEqual(h["days_until"], 0)


class TestAutoCategorize(unittest.TestCase):
    def test_clickbait(self):
        self.assertIn("标题党", failure_manager.auto_categorize("标题党"))
        self.assertIn("标题党", failure_manager.auto_categorize("震惊体"))

    def test_timing(self):
        self.assertIn("时段错", failure_manager.auto_categorize("凌晨3点发布"))
        self.assertIn("时段错", failure_manager.auto_categorize("深夜发布"))

    def test_hook(self):
        self.assertIn("钩子弱", failure_manager.auto_categorize("开头没钩子"))
        self.assertIn("钩子弱", failure_manager.auto_categorize("前3秒跳出"))

    def test_empty(self):
        self.assertEqual(failure_manager.auto_categorize(""), ["其他"])


class TestRenderCardTemplate(unittest.TestCase):
    def test_minimal_render(self):
        card = daily_content.render_card_template(
            today="2026-06-17",
            card_id="TEST-001",
            topic="Test Topic",
            niche="AI",
            platform="抖音",
            region="CN",
            duration="21-34s",
            predicted_views="1000-5000",
            predicted_engagement_rate="3-5%",
            basis="baseline",
            hook_a="Hook A",
            hook_b="Hook B",
        )
        self.assertIn("Test Topic", card)
        self.assertIn("抖音", card)
        self.assertIn("Hook A", card)
        self.assertIn("Hook B", card)
        self.assertIn("type: daily-content-card", card)
        # Frontmatter parseable
        import re, yaml
        m = re.match(r"^---\s*\n(.*?)\n---", card, re.DOTALL)
        self.assertIsNotNone(m, "Frontmatter should be present")
        meta = yaml.safe_load(m.group(1))
        self.assertEqual(meta.get("topic"), "Test Topic")
        self.assertEqual(meta.get("platform"), "抖音")


if __name__ == "__main__":
    unittest.main(verbosity=2)
