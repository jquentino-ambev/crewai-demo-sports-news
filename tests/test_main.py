import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from backend import main


class RunCrewTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_file = Path(self.temp_dir.name) / "report.html"
        self.report_patch = patch.object(main, "REPORT_FILE", self.report_file)
        self.report_patch.start()

    def tearDown(self):
        self.report_patch.stop()
        self.temp_dir.cleanup()

    def test_returns_generated_report(self):
        crew = MagicMock()
        crew.kickoff.side_effect = lambda **_: self.report_file.write_text("<h1>ok</h1>", encoding="utf-8")
        with patch.object(main, "load_crew", return_value=(crew, {})):
            response = main.run_crew(main.RunRequest(tema="futebol brasileiro"))

        self.assertEqual(response.report_html, "<h1>ok</h1>")

    def test_rejects_invalid_theme(self):
        with self.assertRaises(ValidationError):
            main.RunRequest(tema="")

    def test_reports_crew_failure_and_missing_report(self):
        with patch.object(main, "load_crew", side_effect=RuntimeError("indisponível")):
            with self.assertRaisesRegex(HTTPException, "Falha ao executar a crew"):
                main.run_crew(main.RunRequest(tema="futebol"))

        with patch.object(main, "load_crew", return_value=(MagicMock(), {})):
            with self.assertRaisesRegex(HTTPException, "sem gerar report.html"):
                main.run_crew(main.RunRequest(tema="futebol"))

    def test_serializes_execution_and_report_read(self):
        first_started = threading.Event()
        release_first = threading.Event()
        second_started = threading.Event()
        results = []

        first = MagicMock()
        first.kickoff.side_effect = lambda **_: (self.report_file.write_text("primeiro", encoding="utf-8"), first_started.set(), release_first.wait())[2]
        second = MagicMock()
        second.kickoff.side_effect = lambda **_: (second_started.set(), self.report_file.write_text("segundo", encoding="utf-8"))

        with patch.object(main, "load_crew", side_effect=[(first, {}), (second, {})]):
            threads = [threading.Thread(target=lambda: results.append(main.run_crew(main.RunRequest(tema="a")).report_html))]
            threads.append(threading.Thread(target=lambda: results.append(main.run_crew(main.RunRequest(tema="b")).report_html)))
            threads[0].start()
            self.assertTrue(first_started.wait(1))
            threads[1].start()
            self.assertFalse(second_started.wait(0.1))
            release_first.set()
            for thread in threads:
                thread.join(1)

        self.assertEqual(results, ["primeiro", "segundo"])


if __name__ == "__main__":
    unittest.main()
