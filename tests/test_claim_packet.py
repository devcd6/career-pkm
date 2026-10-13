import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_claim_packet.py"
CHECK_SCRIPT = ROOT / "scripts" / "check_claim_packet.py"
CLAIMS_VIEW = ROOT / "kb" / "_views" / "claims.md"
SUMMARIES = ROOT / "kb" / "summaries.md"
SKILLS = ROOT / "kb" / "skills.md"
EDUCATION = ROOT / "kb" / "education.md"
DECISIONS = ROOT / "kb" / "_user_decisions.md"
PACKET_DIR = ROOT / "_work" / "application-packets"
CLAIM_ID = "A-ncmw-project-coordinator-19"
OTHER_CLAIM_ID = "A-ncmw-project-coordinator-119"
SKILL = "Project Tracking (Time Management, Deliverables)"
RULING = "NCMW end date is May 2026."


def run_script(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class ClaimPacketTests(unittest.TestCase):
    def setUp(self):
        PACKET_DIR.mkdir(parents=True, exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=PACKET_DIR)
        self.output = Path(self.temp_dir.name) / "application-facts.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def build_packet(self, claim_ids=CLAIM_ID, *selection_args, output=None):
        return run_script(
            BUILD_SCRIPT,
            "--claims",
            claim_ids,
            *selection_args,
            "--out",
            output or self.output,
        )

    def test_exports_only_selected_claim_with_exact_source_fields(self):
        result = self.build_packet(CLAIM_ID)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        packet_lines = self.output.read_text(encoding="utf-8").splitlines()
        source_lines = CLAIMS_VIEW.read_text(encoding="utf-8").splitlines()
        claim_start = next(i for i, line in enumerate(source_lines) if line.startswith(f"### {CLAIM_ID} |"))
        expected_claim = source_lines[claim_start:claim_start + 3]

        self.assertTrue(all(line in packet_lines for line in expected_claim))
        self.assertTrue(any(line.startswith("## ncmw-project-coordinator") for line in packet_lines))
        self.assertFalse(any(line.startswith(f"### {OTHER_CLAIM_ID} |") for line in packet_lines))
        self.assertEqual(1, len(re.findall(r"^### A-", self.output.read_text(encoding="utf-8"), re.MULTILINE)))
        self.assertTrue(self.output.read_text(encoding="utf-8").startswith("# Application facts packet\n"))

    def test_exports_only_selected_summary_education_skill_and_ruling(self):
        result = self.build_packet(
            CLAIM_ID,
            "--summary", "S-03",
            "--education", "EDU-01,CERT-03",
            "--skill", SKILL,
            "--ruling", RULING,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        packet = self.output.read_text(encoding="utf-8")
        summary_source = SUMMARIES.read_text(encoding="utf-8")
        education_source = EDUCATION.read_text(encoding="utf-8")
        skills_source = SKILLS.read_text(encoding="utf-8")
        decisions_source = DECISIONS.read_text(encoding="utf-8")

        self.assertIn("### S-03", packet)
        self.assertIn("summary: ", packet)
        self.assertIn("source: kb/summaries.md#S-03", packet)
        self.assertNotIn("### S-01", packet)
        self.assertIn("### EDU-01 Bachelor of Arts in Communications", packet)
        self.assertIn("degree: Bachelor of Arts in Communications", packet)
        self.assertIn("### CERT-03 Adult Mental Health First Aid", packet)
        self.assertIn(f"- {SKILL}", packet)
        self.assertIn(f"- {RULING}", packet)
        self.assertIn(SKILL, skills_source)
        self.assertIn(RULING, decisions_source)
        self.assertIn("S-03", summary_source)
        self.assertIn("EDU-01", education_source)

    def test_rejects_unselected_or_unknown_fact_ids_and_skills(self):
        cases = [
            (("--summary", "S-999"), "unknown summary"),
            (("--education", "EDU-999"), "unknown education"),
            (("--skill", "A skill not in the KB"), "unknown skill"),
            (("--ruling", "A ruling not in the decision log"), "unknown ruling"),
        ]
        for args, expected in cases:
            with self.subTest(expected=expected):
                result = self.build_packet(CLAIM_ID, *args)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, (result.stdout + result.stderr).lower())

    def test_rejects_blank_or_fragment_rulings(self):
        for ruling in ("", "  ", "NCMW end date", "the"):
            with self.subTest(ruling=ruling):
                result = self.build_packet(CLAIM_ID, "--ruling", ruling)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("unknown ruling", (result.stdout + result.stderr).lower())

    def test_packet_uses_lf_line_endings(self):
        self.assertEqual(0, self.build_packet().returncode)
        self.assertNotIn(b"\r", self.output.read_bytes())

    def test_parenthesised_variants_block_ends_education_fields(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import build_claim_packet

        with tempfile.TemporaryDirectory() as tmp:
            edu = Path(tmp) / "education.md"
            edu.write_text(
                "### PUB-01 A title\n\ntier: consistent\n\n"
                "variants (raw text as exported):\n- x\ndate: 1999-01-01\n",
                encoding="utf-8",
            )
            entry = build_claim_packet.parse_education(edu)["PUB-01"]
        self.assertEqual("consistent", entry["tier"])
        self.assertNotIn("date", entry)

    def test_rejects_packet_output_outside_knowledge_repo(self):
        outside = Path(self.temp_dir.name).parent.parent / f"outside-{Path(self.temp_dir.name).name}.md"

        result = self.build_packet(output=outside)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("_work/application-packets", (result.stdout + result.stderr).replace("\\", "/"))
        self.assertFalse(outside.exists())

    def test_rejects_unknown_claim_ids(self):
        result = self.build_packet("A-not-a-real-role-999")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown", (result.stdout + result.stderr).lower())

    def test_rejects_duplicate_claim_ids(self):
        result = self.build_packet(f"{CLAIM_ID},{CLAIM_ID}")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("duplicate", (result.stdout + result.stderr).lower())

    def test_rejects_empty_claim_selection(self):
        result = self.build_packet("")

        self.assertNotEqual(0, result.returncode)

    def test_checker_accepts_exported_packet(self):
        build_result = self.build_packet(CLAIM_ID)
        self.assertEqual(0, build_result.returncode, build_result.stdout + build_result.stderr)

        result = run_script(CHECK_SCRIPT, self.output)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_checker_rejects_changed_claim_text(self):
        build_result = self.build_packet(CLAIM_ID)
        self.assertEqual(0, build_result.returncode, build_result.stdout + build_result.stderr)
        packet = self.output.read_text(encoding="utf-8")
        self.output.write_text(packet.replace("canonical: ", "canonical: edited ", 1), encoding="utf-8")

        result = run_script(CHECK_SCRIPT, self.output)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("mismatch", result.stdout.lower())

    def test_checker_rejects_missing_metrics_field(self):
        build_result = self.build_packet(CLAIM_ID)
        self.assertEqual(0, build_result.returncode, build_result.stdout + build_result.stderr)
        packet_lines = self.output.read_text(encoding="utf-8").splitlines()
        self.output.write_text(
            "\n".join(line for line in packet_lines if not line.startswith("metrics:")) + "\n",
            encoding="utf-8",
        )

        result = run_script(CHECK_SCRIPT, self.output)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing metrics", result.stdout.lower())

    def test_checker_rejects_changed_selected_summary(self):
        build_result = self.build_packet(CLAIM_ID, "--summary", "S-03")
        self.assertEqual(0, build_result.returncode, build_result.stdout + build_result.stderr)
        packet = self.output.read_text(encoding="utf-8")
        self.output.write_text(packet.replace("summary: ", "summary: edited ", 1), encoding="utf-8")

        result = run_script(CHECK_SCRIPT, self.output)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("summary mismatch", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
