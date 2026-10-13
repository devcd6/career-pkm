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
CLAIM_ID = "A-ncmw-project-coordinator-19"
OTHER_CLAIM_ID = "A-ncmw-project-coordinator-119"


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
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self.temp_dir.name) / "claims-packet.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def build_packet(self, claim_ids):
        return run_script(
            BUILD_SCRIPT,
            "--claims",
            claim_ids,
            "--out",
            self.output,
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


if __name__ == "__main__":
    unittest.main()
