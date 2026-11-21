"""Tạo bản đóng gói phát hành từ ĐÚNG một commit (TICKET-04 mục 1, "Đóng gói và phát hành"). Chủ file: Tâm.

    python3 tools/package_release.py                      # đóng gói HEAD -> dist/quan-an-cho-noi-v1.0.0.zip
    python3 tools/package_release.py --ref phase-4 --check  # đóng gói tag phase-4 rồi chạy thử bản giải nén

- Dùng `git archive` nên gói chỉ chứa file đã commit ở `--ref` (không lẫn file tạm, .git, kho/out local).
- Ghi kèm `<zip>.sha256` và in commit đã đóng gói để đối chiếu với tag / Release.
- `--check`: giải nén vào thư mục tạm và chạy headless gather + day từ CHÍNH bản giải nén (mã 0, có dòng end).
Chỉ dùng thư viện chuẩn Python + lệnh `git`.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "quan-an-cho-noi"

# File bắt buộc có trong gói để chạy được theo README (giao diện, headless, test).
REQUIRED = ["README.md", "LICENSE", "CREDITS.md", "CHANGELOG.md", "game.contract.json",
            "chonoi/live.py", "chonoi/headless.py", "chonoi/web/index.html", "tests/helpers.py"]


class PackageError(Exception):
    """Gói không hợp lệ (thiếu file bắt buộc...)."""


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def build(ref="HEAD", version="v1.0.0", out_dir=None):
    """Đóng gói `ref` thành zip; trả (đường dẫn zip, commit sha)."""
    sha = git("rev-parse", f"{ref}^{{commit}}")
    out_dir = out_dir or os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    prefix = f"{NAME}-{version}"
    zpath = os.path.join(out_dir, f"{prefix}.zip")
    git("archive", "--format=zip", f"--prefix={prefix}/", "-o", zpath, sha)
    with zipfile.ZipFile(zpath) as z:
        names = set(z.namelist())
    missing = [f for f in REQUIRED if f"{prefix}/{f}" not in names]
    if missing:
        raise PackageError(f"gói từ {ref} ({sha[:7]}) thiếu file bắt buộc: {missing} — đã commit chưa?")
    with open(zpath, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    with open(zpath + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{digest}  {os.path.basename(zpath)}\n")
    return zpath, sha


def check(zpath):
    """Giải nén vào thư mục tạm và chạy headless từ bản giải nén. Trả danh sách lỗi (rỗng = đạt)."""
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        (top,) = os.listdir(tmp)
        app = os.path.join(tmp, top)
        runs = {"gather": ["--mode", "gather", "--seed", "1", "--ticks", "120"],
                "day": ["--mode", "day", "--days", "1", "--seed", "1", "--ticks", "40000"]}
        for name, args in runs.items():
            out = os.path.join(tmp, f"{name}.jsonl")
            p = subprocess.run([sys.executable, "-m", "chonoi.headless", *args, "--out", out],
                               cwd=app, capture_output=True, text=True)
            if p.returncode != 0:
                errors.append(f"{name}: mã {p.returncode}: {p.stderr.strip()[:300]}")
                continue
            with open(out, encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]
            if not rows or rows[-1].get("type") != "end":
                errors.append(f"{name}: thiếu dòng end")
    return errors


def main(argv=None):
    p = argparse.ArgumentParser(description="Đóng gói bản phát hành từ một commit")
    p.add_argument("--ref", default="HEAD", help="commit / tag cần đóng gói (mặc định HEAD)")
    p.add_argument("--version", default="v1.0.0")
    p.add_argument("--out-dir", default=None, help="thư mục ra (mặc định dist/)")
    p.add_argument("--check", action="store_true", help="giải nén và chạy thử headless từ bản đóng gói")
    a = p.parse_args(argv)
    try:
        zpath, sha = build(a.ref, a.version, a.out_dir)
    except PackageError as e:
        print("LỖI", e)
        return 1
    print(f"đã đóng gói {a.ref} ({sha}) -> {zpath}")
    if a.check:
        errors = check(zpath)
        for e in errors:
            print("LỖI", e)
        if errors:
            return 1
        print("kiểm bản giải nén: gather + day chạy được (mã 0, có dòng end)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
