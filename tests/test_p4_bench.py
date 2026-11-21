"""Phase 4: contract và smoke cho benchmark render của Huyền."""

import json
import os
import tempfile
import unittest
from unittest import mock

from chonoi import bench
from helpers import ROOT


class BenchUnit(unittest.TestCase):
    def test_browser_command_fixes_1280x720_and_headless(self):
        command = bench.browser_command("browser", "profile", "http://127.0.0.1:1/")
        self.assertIn("--headless=new", command)
        self.assertIn("--no-sandbox", command)
        self.assertIn("--window-size=1280,720", command)
        self.assertIn("--force-device-scale-factor=1", command)
        adjusted = bench.browser_command("browser", "profile", "url", 1298, 816)
        self.assertIn("--window-size=1298,816", adjusted)

    def test_instrumented_page_uses_renderer_and_warmup(self):
        html = bench._instrumented_html(0.25).decode("utf-8")
        self.assertIn("<canvas id=\"c\">", html)
        self.assertIn("drawGather(w, h)", html)
        self.assertIn("const warmupMs = 3000", html)
        self.assertIn("const durationMs = 250.0", html)
        self.assertIn("requestAnimationFrame(sample)", html)

    def test_atomic_output_has_exact_five_fields(self):
        value = {"avg_fps": 60.0, "p1_low_fps": 55.0, "frames": 60,
                 "measured_s": 1.0, "load_ms": 12.5}
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bench.json")
            bench._write_json_atomic(path, value)
            with open(path, encoding="utf-8") as source:
                saved = json.load(source)
            self.assertEqual(saved, value)
            self.assertEqual(set(saved), set(bench.FIELDS))
            self.assertEqual(os.listdir(directory), ["bench.json"])

    def test_cli_validation_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bench.json")
            with self.assertRaises(SystemExit) as caught:
                bench.main(["--seed", "1", "--duration", "0", "--out", path])
            self.assertEqual(caught.exception.code, 2)
            self.assertFalse(os.path.exists(path))

    def test_cli_prints_and_writes_runner_result(self):
        result = {"avg_fps": 60.0, "p1_low_fps": 58.0, "frames": 60,
                  "measured_s": 1.0, "load_ms": 20.0}
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bench.json")
            with mock.patch.object(bench, "run_benchmark", return_value=result) as run:
                self.assertEqual(bench.main(["--seed", "7", "--duration", "1", "--out", path]), 0)
            run.assert_called_once_with(7, 1.0, path)


class BenchArtifact(unittest.TestCase):
    def test_committed_run_has_contract_shape_and_full_duration(self):
        path = os.path.join(ROOT, "docs", "proof", "phase-4", "bench.json")
        with open(path, encoding="utf-8") as source:
            result = json.load(source)

        self.assertEqual(set(result), set(bench.FIELDS))
        self.assertGreaterEqual(result["measured_s"], 30)
        self.assertGreater(result["frames"], 0)
        self.assertGreater(result["avg_fps"], 0)
        self.assertGreater(result["p1_low_fps"], 0)
        self.assertGreater(result["load_ms"], 0)


if __name__ == "__main__":
    unittest.main()
