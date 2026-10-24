import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_claim_packet as bcp  # noqa: E402
import check_application as ca  # noqa: E402


class PhraseMatchingTests(unittest.TestCase):
    def test_curly_apostrophe_in_phrase_matches(self):
        self.assertTrue(ca.has_phrase("Associate's degree", "Associate’s Degree"))

    def test_variant_phrase_handles_inflection_and_hyphen(self):
        self.assertTrue(ca.variant_phrase("Prepared the agenda", "prepare"))
        self.assertTrue(ca.variant_phrase("provided assistance", "assist"))
        self.assertTrue(ca.variant_phrase("Troubleshooting issues", "trouble-shoot"))
        self.assertTrue(ca.variant_phrase("quarterly reports", "report"))

    def test_variant_phrase_rejects_unrelated_text(self):
        self.assertFalse(ca.variant_phrase("managed a budget", "message"))
        self.assertFalse(ca.variant_phrase("recorded minutes", "meeting minutes"))

    def test_unknown_category_lines_flags_typos_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "keywords.txt"
            path.write_text("Hard Skill | Zoom\nHard Filters | Associate's Degree\nplain phrase\n", encoding="utf-8")
            self.assertEqual(["Hard Filters | Associate's Degree"], ca.unknown_category_lines(path))


class SkillParsingTests(unittest.TestCase):
    def test_skill_lines_only_and_flags_carried(self):
        flags = bcp.parse_skill_flags()
        self.assertFalse([name for name in flags if name.startswith(("Line format", "- "))])
        self.assertIn("user-confirmed", flags["LMS platforms (LearnWorlds, Rise360, iSpring)"])

    def test_skill_match_is_case_insensitive(self):
        flags = bcp.parse_skill_flags()
        self.assertEqual("Google Workspace", bcp.match_skill("google workspace", flags))
        self.assertIsNone(bcp.match_skill("A skill not in the KB", flags))


class RankReportTests(unittest.TestCase):
    def test_report_lists_near_matches_skills_and_hard_filters(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "jd.md").write_text("Prepare reports. Microsoft Office. Associate's Degree. T1 background check.", encoding="utf-8")
            (folder / "keywords.txt").write_text(
                "Action Keyword | prepare\nHard Skill | Microsoft Office\nHard Filter | Associate's Degree\n"
                "Hard Filter | T1 background check\nHard Filters | typo\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "rank_claims.py"), "--jd", str(folder / "jd.md"),
                 "--keywords", str(folder / "keywords.txt")], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            out = result.stdout
            self.assertIn("inflected or hyphenated form in A-", out)
            self.assertRegex(out, r"Microsoft Office \[Hard Skill\] \| in kb/skills\.md:\d+")
            self.assertIn("EDU-02", out)
            self.assertIn("eligibility: no KB source", out)
            self.assertIn("WARNING: unknown keyword category", out)


if __name__ == "__main__":
    unittest.main()
