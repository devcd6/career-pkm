import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RANK_SCRIPT = ROOT / "scripts" / "rank_claims.py"
CLAIMS_VIEW = ROOT / "kb" / "_views" / "claims.md"


class RankClaimsTests(unittest.TestCase):
    def test_claim_ranking_accepts_jd_and_keywords_without_application_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source_lines = CLAIMS_VIEW.read_text(encoding="utf-8").splitlines()
            first_claim = next(i for i, line in enumerate(source_lines) if line.startswith("canonical: "))
            canonical = re.sub(r"\[[^\]]*\]", " ", source_lines[first_claim][11:])
            phrase = " ".join(re.findall(r"[A-Za-z]+", canonical)[:3])
            jd = folder / "jd.md"
            keywords = folder / "keywords.txt"
            output = folder / "rank.md"
            jd.write_text(phrase, encoding="utf-8")
            keywords.write_text(f"Hard Skill | {phrase}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(RANK_SCRIPT),
                    "--jd",
                    str(jd),
                    "--keywords",
                    str(keywords),
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(output.exists())
            self.assertRegex(output.read_text(encoding="utf-8"), r"- A-[\w-]+")


if __name__ == "__main__":
    unittest.main()
