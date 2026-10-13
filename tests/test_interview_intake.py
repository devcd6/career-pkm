import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "scripts" / "import_interview_packet.py"
CLAIM_ID = "A-ncmw-project-coordinator-19"

PACKET = f"""# Interview packet: 2026-10-13_org_role

slug: 2026-10-13_org_role
created: 2026-10-13

## Job description
#### Coordinator
Support programs.

## Submitted resume
- Managed member communications.

## Claims used
- {CLAIM_ID}

## Role research
Source: https://example.org/about (seen 2026-10-13)

## Known gaps
- No grant writing.
"""


def run(*args):
    return subprocess.run([sys.executable, str(INTAKE), *map(str, args)], cwd=ROOT, capture_output=True, text=True)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / "interviews"
        self.src = Path(self.tmp.name) / "packet.md"

    def intake(self, text=PACKET):
        self.src.write_text(text, encoding="utf-8")
        return run(self.src, "--dest-root", self.dest)

    def test_valid_packet_is_stored_unchanged(self):
        r = self.intake()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        stored = self.dest / "2026-10-13_org_role" / "packet.md"
        self.assertEqual(stored.read_text(encoding="utf-8"), PACKET)

    def test_incomplete_packets_rejected_and_nothing_stored(self):
        cases = {
            "no resume": PACKET.replace("## Submitted resume", "## Resume"),
            "no claims mapping": PACKET.replace(f"- {CLAIM_ID}", "- none"),
            "no gaps": PACKET.replace("- No grant writing.", ""),
            "no sources": PACKET.replace("https://example.org/about", "example"),
            "extra file section": PACKET + "\n## Cover letter\ntext\n",
        }
        for name, text in cases.items():
            with self.subTest(name):
                r = self.intake(text)
                self.assertNotEqual(r.returncode, 0)
                self.assertFalse(self.dest.exists())

    def test_unknown_claim_id_rejected(self):
        r = self.intake(PACKET.replace(CLAIM_ID, "A-ncmw-project-coordinator-99999"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("A-ncmw-project-coordinator-99999", r.stdout)
        self.assertFalse(self.dest.exists())

    def test_unsafe_slug_rejected(self):
        r = self.intake(PACKET.replace("slug: 2026-10-13_org_role", "slug: ../../kb"))
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.dest.exists())

    def test_existing_import_not_overwritten(self):
        self.assertEqual(self.intake().returncode, 0)
        r = self.intake(PACKET.replace("No grant writing", "Changed"))
        self.assertNotEqual(r.returncode, 0)
        stored = self.dest / "2026-10-13_org_role" / "packet.md"
        self.assertEqual(stored.read_text(encoding="utf-8"), PACKET)


if __name__ == "__main__":
    unittest.main()
