"""Verify the issue generator without contacting GitHub or using real credentials."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = Path("docs/02_planificacion/PLAN_SDD.md")
FICHAS = (
    "docs/04_integrantes/A/TAREAS_A.md",
    "docs/04_integrantes/B/TAREAS_B.md",
    "docs/04_integrantes/Angel_Zambrano/TAREAS_C.md",
)


class TestCrearIssues(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.script = self.root / "scripts/crear_issues.sh"
        self.script.parent.mkdir()
        shutil.copy2(ROOT / "scripts/crear_issues.sh", self.script)
        for relative in (str(PLAN), *FICHAS):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        binary = self.root / "bin"
        binary.mkdir()
        self.log = self.root / "gh.jsonl"
        fake = binary / "gh"
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import json, os, pathlib, sys\n"
            "p = pathlib.Path(os.environ['FAKE_GH_LOG'])\n"
            "history = [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []\n"
            "args = sys.argv[1:]\n"
            "with p.open('a') as stream: stream.write(json.dumps(args) + '\\n')\n"
            "if args[:2] == ['repo', 'view']:\n"
            " print(json.dumps({'nameWithOwner': 'equipo/energia', 'url': 'https://example.invalid/energia'}))\n"
            "elif args[:2] == ['issue', 'list']:\n"
            " print('[{\"number\": 1}]' if os.environ.get('FAKE_EXISTING') else '[]')\n"
            "elif args[:2] == ['issue', 'create']:\n"
            " number = 1001 + sum(x[:2] == ['issue', 'create'] for x in history)\n"
            " print('https://example.invalid/energia/issues/' + str(number))\n"
        )
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""),
                        GH_USER_A="usuario-a", GH_USER_B="usuario-b", GH_USER_C="usuario-angel",
                        FAKE_GH_LOG=str(self.log), DRY_RUN="0")

    def run_script(self, *args, **env_changes):
        return subprocess.run(["/bin/bash", str(self.script), *args], check=False, cwd=self.root,
                              env=dict(self.env, **env_changes), capture_output=True, text=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_dry_run_includes_all_models_and_final_deliverables_without_github(self):
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        ids = re.findall(r"^\[dry-run\] ([A-Z]+-\d+) \|", result.stdout, re.MULTILINE)
        self.assertEqual(len(ids), 50)
        self.assertEqual(len(set(ids)), 50)
        self.assertTrue({f"{model}-{step}" for model in ("LR", "RF", "XG")
                         for step in range(1, 8)} <= set(ids))
        self.assertIn("6 a 8 diapositivas", result.stdout)
        self.assertIn("8 a 10 minutos", result.stdout)
        self.assertEqual(self.calls(), [])

    def test_invalid_dependencies_are_rejected_before_github(self):
        cases = {
            "missing": "| T-00 | Inicio | C | T-99 | Repo |",
            "cycle": "| T-00 | Inicio | C | T-01 | Repo |\n| T-01 | Contrato | A+B+C | T-00 | Spec |",
            "duplicate": "| T-00 | Inicio | C | - | Repo |\n| T-00 | Otra | A | - | Spec |",
        }
        for name, rows in cases.items():
            with self.subTest(name=name):
                (self.root / PLAN).write_text("### Fase 0 — Fundación\n" + rows + "\n")
                result = self.run_script()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Error:", result.stderr)
                self.assertEqual(self.calls(), [])

    def test_existing_issues_stop_publication_before_any_mutation(self):
        result = self.run_script(FAKE_EXISTING="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ya tiene issues", result.stderr)
        self.assertEqual([call[:2] for call in self.calls()], [["repo", "view"], ["issue", "list"]])

    def test_fake_publication_preserves_owners_and_resolves_dependency_numbers(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        creates = [call for call in self.calls() if call[:2] == ["issue", "create"]]
        edits = [call for call in self.calls() if call[:2] == ["issue", "edit"]]
        self.assertEqual(len(creates), 50)
        self.assertEqual(len(edits), 50)
        numbers, by_id = {}, {}
        for number, call in enumerate(creates, 1001):
            task_id = re.match(r"\[([^]]+)\]", call[call.index("--title") + 1])[1]
            numbers[task_id], by_id[task_id] = str(number), call
        self.assertEqual(by_id["T-03"].count("--assignee"), 1)
        self.assertIn("usuario-a", by_id["T-03"])
        self.assertIn("usuario-angel", by_id["XG-6"])
        xg_edit = next(call for call in edits if call[2] == numbers["XG-6"])
        body = xg_edit[xg_edit.index("--body") + 1]
        for dependency in ("XG-5", "MC-4", "DB-2"):
            self.assertIn("#" + numbers[dependency] + " (" + dependency + ")", body)
