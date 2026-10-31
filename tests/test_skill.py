"""Checks for the medical-research-council skill. Run: python3 -m unittest discover -s tests -v"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "medical-research-council"
SCORE = SKILL / "scripts" / "score.py"
CHECK = SKILL / "scripts" / "check_refs.py"


def frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md has no frontmatter"
    fields = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([a-z-]+):\s*(.*)", line)
        if km:
            fields[km.group(1)] = km.group(2).strip().strip('"')
    return fields


def run(*args, cwd=None, env=None):
    return subprocess.run(list(args), cwd=cwd, env=env, capture_output=True, text=True)


class TestFrontmatter(unittest.TestCase):
    def test_name_matches_folder(self):
        self.assertEqual(frontmatter()["name"], SKILL.name)

    def test_description(self):
        desc = frontmatter()["description"]
        self.assertTrue(desc.startswith("Use when"))
        self.assertLessEqual(len(desc), 1024)

    def test_versions_match(self):
        version = frontmatter()["version"]
        manifests = [
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / "gemini-extension.json",
        ]
        for path in manifests:
            self.assertEqual(json.loads(path.read_text())["version"], version, path.name)
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(market["plugins"][0]["version"], version)

    def test_referenced_files_exist(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for ref in set(re.findall(r"`((?:references|scripts)/[\w.-]+)`", text)) | {"roster.json"}:
            self.assertTrue((SKILL / ref).exists(), ref)


class TestRoster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = json.loads((SKILL / "roster.json").read_text())
        cls.keys = {s["key"] for s in cls.roster["seats"]}

    def test_boards_sum_to_100_and_use_known_seats(self):
        for name, board in self.roster["boards"].items():
            self.assertEqual(sum(board["full"].values()), 100, name)
            self.assertTrue(set(board["full"]) <= self.keys, name)
            self.assertTrue(set(board["quick"]) <= self.keys, name)

    def test_veto_seats_sit_on_every_board(self):
        for name, board in self.roster["boards"].items():
            for v in self.roster["veto_seats"]:
                self.assertIn(v, board["full"], name)
                self.assertIn(v, board["quick"], name)

    def test_every_seat_has_a_lens_card(self):
        seats_md = (SKILL / "references" / "seats.md").read_text(encoding="utf-8")
        for seat in self.roster["seats"]:
            self.assertIn(f"### {seat['short']}:", seats_md, seat["key"])


class TestScore(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        scoring = (SKILL / "references" / "scoring.md").read_text(encoding="utf-8")
        self.example = json.loads(re.search(r"```json\n(.*?)```", scoring, re.S).group(1))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def score(self, data):
        (self.tmp / "scores.json").write_text(json.dumps(data))
        return run(sys.executable, str(SCORE), str(self.tmp))

    def test_documented_example(self):
        r = self.score(self.example)
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads((self.tmp / "scores-result.json").read_text())
        self.assertEqual(result["ranking"][0], "B")
        self.assertEqual(result["options"]["A"]["final"], 4.0)
        self.assertTrue(result["options"]["A"]["cap_fired"])
        self.assertEqual(result["options"]["B"]["verdict"], "GO WITH CONDITIONS")

    def test_default_weights_from_roster(self):
        data = dict(self.example)
        del data["weights"]
        self.assertEqual(self.score(data).returncode, 0)

    def test_quick_board_renormalises(self):
        data = {"type": "protocol", "options": {"A": "x"},
                "seats": {k: {"scores": {"A": 8.0}} for k in ("evidence", "ethics", "methods")}}
        self.assertEqual(self.score(data).returncode, 0)
        result = json.loads((self.tmp / "scores-result.json").read_text())
        self.assertAlmostEqual(sum(result["weights"].values()), 100, delta=0.5)
        self.assertEqual(result["options"]["A"]["verdict"], "GO")

    def test_non_veto_seat_cannot_veto(self):
        data = json.loads(json.dumps(self.example))
        data["seats"]["patient"]["vetoes"] = ["B"]
        r = self.score(data)
        self.assertIn("not a veto seat", r.stderr)
        result = json.loads((self.tmp / "scores-result.json").read_text())
        self.assertEqual(result["options"]["B"]["vetoed_by"], [])

    def test_rejects_out_of_range_score(self):
        data = json.loads(json.dumps(self.example))
        data["seats"]["methods"]["scores"]["A"] = 11
        self.assertNotEqual(self.score(data).returncode, 0)


class TestCheckRefs(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "evidence.md").write_text("- PMID: 12345678\n- NCT01234567\n- DOI: 10.1000/xyz.123\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_pass(self):
        (self.tmp / "verdict.md").write_text("PMID 12345678, NCT01234567, https://doi.org/10.1000/xyz.123.\n")
        self.assertEqual(run(sys.executable, str(CHECK), str(self.tmp)).returncode, 0)

    def test_fail_on_invented_reference(self):
        (self.tmp / "verdict.md").write_text("PMID: 99999999\n")
        r = run(sys.executable, str(CHECK), str(self.tmp))
        self.assertEqual(r.returncode, 1)
        self.assertIn("99999999", r.stdout)


@unittest.skipIf(os.name == "nt", "install.sh needs bash")
class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.env = dict(os.environ, HOME=str(self.home))

    def tearDown(self):
        shutil.rmtree(self.home)

    def test_install_all_then_uninstall(self):
        r = run("bash", str(ROOT / "install.sh"), "--all", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        for d in (".claude/skills", ".agents/skills"):
            self.assertTrue((self.home / d / "medical-research-council" / "SKILL.md").exists(), d)
        r = run("bash", str(ROOT / "install.sh"), "--all", "--uninstall", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.home / ".claude/skills/medical-research-council").exists())

    def test_link_mode(self):
        r = run("bash", str(ROOT / "install.sh"), "--codex", "--link", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.home / ".agents/skills/medical-research-council").is_symlink())


class TestAnonymizeAndRender(unittest.TestCase):
    EXAMPLE = ROOT / "examples" / "2026-10-31-sglt2i-ca-aki-pci"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name in ("round-1.md", "round-2.md", "verdict.md", "scores.json", "evidence.md"):
            shutil.copy(self.EXAMPLE / name, self.tmp / name)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_anonymize_hides_seat_names(self):
        r = run(sys.executable, str(SKILL / "scripts" / "anonymize.py"), str(self.tmp), "--seed", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        anon = (self.tmp / "round-2-anon.md").read_text()
        self.assertEqual(len(re.findall(r"^## Response \d$", anon, re.M)), 5)
        for seat in ("## Evidence", "## Methods", "## Ethics", "## Patient", "## Feasibility", "Chair notes"):
            self.assertNotIn(seat, anon)
        self.assertEqual(r.stdout.count("Response "), 5)

    def test_example_scores_and_refs(self):
        self.assertEqual(run(sys.executable, str(SCORE), str(self.tmp)).returncode, 0)
        self.assertEqual(run(sys.executable, str(CHECK), str(self.tmp)).returncode, 0)

    def test_render_report_is_self_contained(self):
        run(sys.executable, str(SCORE), str(self.tmp))
        r = run(sys.executable, str(SKILL / "scripts" / "render_report.py"), str(self.tmp))
        self.assertEqual(r.returncode, 0, r.stderr)
        page = (self.tmp / "report.html").read_text()
        self.assertIn("MAJOR REVISION", page)
        self.assertIn("veto cap fired", page)
        self.assertNotRegex(page, r"<(script|link)[^>]+(src|href)=\"http")


if __name__ == "__main__":
    unittest.main()
