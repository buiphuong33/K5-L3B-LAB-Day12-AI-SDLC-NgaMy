"""Phase 4 — đóng gói và README (TICKET-04 mục 1 "Đóng gói và phát hành"). Chủ lát: Tâm.

- README có đủ: yêu cầu môi trường, chạy giao diện từ clone sạch trong tối đa 3 lệnh, điều khiển,
  lệnh test, lệnh headless, benchmark (và soak).
- LICENSE, CREDITS.md có mặt và có nội dung.
- `tools/package_release.py` đóng gói HEAD từ git, gói có file bắt buộc, không lẫn .git / dist /
  file kho-out local, và bản giải nén chạy được headless.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from helpers import ROOT

sys.path.insert(0, os.path.join(ROOT, "tools"))
import package_release  # noqa: E402


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def section(text, title):
    """Nội dung mục `## <title>...` tới mục `## ` kế tiếp."""
    m = re.search(rf"^## {re.escape(title)}.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def is_git_checkout():
    return shutil.which("git") is not None and os.path.isdir(os.path.join(ROOT, ".git"))


class Readme(unittest.TestCase):
    TEXT = read("README.md")

    def test_has_required_sections(self):
        for title in ("Chạy nhanh", "Yêu cầu môi trường", "Điều khiển", "Chạy test", "Headless", "Benchmark"):
            self.assertTrue(section(self.TEXT, title).strip(), f"README thiếu mục '## {title}'")

    def test_quickstart_is_at_most_three_commands_and_runs_ui(self):
        block = re.search(r"```(?:bash|sh)?\n(.*?)```", section(self.TEXT, "Chạy nhanh"), re.S)
        self.assertIsNotNone(block, "mục Chạy nhanh cần một khối lệnh")
        cmds = [ln for ln in block.group(1).splitlines() if ln.strip() and not ln.strip().startswith("#")]
        self.assertLessEqual(len(cmds), 3, cmds)
        self.assertTrue(cmds[0].strip().startswith("git clone"), cmds)
        self.assertIn("chonoi.live", cmds[-1])

    def test_mentions_headless_test_bench_and_soak_commands(self):
        for needle in ("python3 -m chonoi.headless", "unittest discover", "bench_cmd", "soak_cmd",
                       "--seed 42 --duration 30 --out bench.json", "--seed 7 --days 10 --out soak.json"):
            self.assertIn(needle, self.TEXT)


class LicenseAndCredits(unittest.TestCase):
    def test_license_is_mit_with_holder(self):
        text = read("LICENSE")
        self.assertIn("MIT License", text)
        self.assertRegex(text, r"Copyright \(c\) \d{4} ")

    def test_credits_lists_starter_assets_and_ai_tools(self):
        text = read("CREDITS.md")
        for needle in ("VinUni-AI20k", "Asset ngoài", "Công cụ AI"):
            self.assertIn(needle, text)


@unittest.skipUnless(is_git_checkout(), "cần git checkout để đóng gói bằng git archive")
class PackageRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.zpath, cls.sha = package_release.build("HEAD", "v1.0.0", cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_package_is_built_from_head_with_checksum(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertEqual(self.sha, head)
        self.assertTrue(os.path.exists(self.zpath + ".sha256"))

    def test_package_has_required_files_and_no_local_junk(self):
        with zipfile.ZipFile(self.zpath) as z:
            names = z.namelist()
        prefix = "quan-an-cho-noi-v1.0.0/"
        self.assertTrue(all(n.startswith(prefix) for n in names))
        for f in package_release.REQUIRED:
            self.assertIn(prefix + f, names)
        for n in names:
            rel = n[len(prefix):]
            self.assertFalse(rel.startswith((".git/", "dist/")), n)
            self.assertFalse(rel.endswith((".jsonl", ".env")), n)

    def test_unpacked_package_runs_headless(self):
        self.assertEqual(package_release.check(self.zpath), [])


if __name__ == "__main__":
    unittest.main()
