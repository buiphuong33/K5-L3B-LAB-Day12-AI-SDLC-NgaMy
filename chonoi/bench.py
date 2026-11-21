"""Benchmark renderer thật ở 1280x720 bằng Chrome/Edge headless.

    python3 -m chonoi.bench --seed 1 --duration 30 --out bench.json

Chỉ dùng thư viện chuẩn Python. Trình duyệt tải đúng trang web của game, chờ 3 giây,
đo requestAnimationFrame trong khoảng yêu cầu rồi POST số đo về server tạm.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .contract import load_contract
from .live import LiveGame, WEB_DIR

WIDTH = 1280
HEIGHT = 720
WARMUP_S = 3.0
FIELDS = ("avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"lỗi: {message}\n")
        raise SystemExit(2)


def _positive_duration(value):
    try:
        duration = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("duration phải là số")
    if not math.isfinite(duration) or duration <= 0:
        raise argparse.ArgumentTypeError("duration phải > 0")
    return duration


def find_browser():
    configured = os.environ.get("CHONOI_BROWSER")
    if configured:
        return configured if os.path.isfile(configured) else shutil.which(configured)
    for command in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
        path = shutil.which(command)
        if path:
            return path
    candidates = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    )
    return next((path for path in candidates if os.path.isfile(path)), None)


def browser_command(browser, profile, url, width=WIDTH, height=HEIGHT):
    return [browser, "--headless=new", "--no-first-run", "--no-default-browser-check",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={width},{height}",
            f"--user-data-dir={profile}", url]


def _instrumented_html(duration):
    with open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8") as source:
        html = source.read()
    script = """
(() => {
  const warmupMs = 3000;
  const durationMs = __DURATION_MS__;
  let loadedAt = null, measureAt = null, sent = false;
  let viewportSent = false;
  const samples = [];
  function finish() {
    if (sent || samples.length < 2) return;
    sent = true;
    const deltas = samples.slice(1).map((v, i) => v - samples[i]).filter((v) => v > 0);
    const measuredMs = deltas.reduce((a, b) => a + b, 0);
    const slow = deltas.slice().sort((a, b) => b - a).slice(0, Math.max(1, Math.ceil(deltas.length * 0.01)));
    const slowMean = slow.reduce((a, b) => a + b, 0) / slow.length;
    const result = {
      avg_fps: Math.round((deltas.length * 1000000 / measuredMs)) / 1000,
      p1_low_fps: Math.round((1000 / slowMean) * 1000) / 1000,
      frames: deltas.length,
      measured_s: Math.round((measuredMs / 1000) * 1000) / 1000,
      load_ms: Math.round(loadedAt * 1000) / 1000,
      viewport: [innerWidth, innerHeight]
    };
    fetch('/bench-result', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(result)});
  }
  function sample(ts) {
    if (!viewportSent) {
      viewportSent = true;
      fetch('/bench-viewport', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify([innerWidth, innerHeight])});
    }
    if (snap && innerWidth === 1280 && innerHeight === 720 && loadedAt === null) {
      loadedAt = ts; measureAt = ts + warmupMs;
    }
    if (measureAt !== null && ts >= measureAt) samples.push(ts);
    if (measureAt !== null && ts >= measureAt + durationMs) finish();
    if (!sent) requestAnimationFrame(sample);
  }
  requestAnimationFrame(sample);
})();
""".replace("__DURATION_MS__", repr(duration * 1000.0))
    return html.replace("</script>", script + "\n</script>", 1).encode("utf-8")


class _ResultBox:
    def __init__(self):
        self.value = None
        self.error = None
        self.ready = threading.Event()
        self.viewport = None
        self.viewport_ready = threading.Event()


class _BenchServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def _handler_type(game, html, box):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body, content_type="application/json; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, html, "text/html; charset=utf-8")
            elif path == "/state":
                self._send(200, game.state_json())
            else:
                self._send(404, b'{}')

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            if path not in ("/bench-result", "/bench-viewport"):
                self._send(404, b'{}')
                return
            try:
                size = int(self.headers.get("Content-Length") or 0)
                data = json.loads(self.rfile.read(size).decode("utf-8"))
                if path == "/bench-viewport":
                    if (not isinstance(data, list) or len(data) != 2 or
                            any(not isinstance(value, int) or value <= 0 for value in data)):
                        raise ValueError("viewport không hợp lệ")
                    box.viewport = data
                    box.viewport_ready.set()
                    self._send(200, b'{"ok":true}')
                    return
                viewport = data.pop("viewport", None)
                if viewport != [WIDTH, HEIGHT]:
                    raise ValueError(f"viewport {viewport!r} không phải {WIDTH}x{HEIGHT}")
                if set(data) != set(FIELDS):
                    raise ValueError("kết quả benchmark sai schema")
                if (not isinstance(data["frames"], int) or data["frames"] <= 0 or
                        any(not isinstance(data[key], (int, float)) or not math.isfinite(data[key]) or data[key] <= 0
                            for key in FIELDS if key != "frames")):
                    raise ValueError("kết quả benchmark có số đo không hợp lệ")
                box.value = {key: data[key] for key in FIELDS}
                self._send(200, b'{"ok":true}')
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                box.error = str(exc)
                self._send(400, b'{"ok":false}')
            finally:
                if path == "/bench-result":
                    box.ready.set()
                elif box.error:
                    box.viewport_ready.set()

    return Handler


def _write_json_atomic(path, value):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".bench-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, ensure_ascii=False, separators=(",", ":"))
            output.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def run_benchmark(seed, duration, out_path, browser=None):
    browser = browser or find_browser()
    if not browser:
        raise RuntimeError("không tìm thấy Chrome/Chromium/Edge; đặt CHONOI_BROWSER tới file trình duyệt")
    tuning = load_contract()["tuning"]
    game = LiveGame("gather", tuning, {}, seed)
    box = _ResultBox()
    html = _instrumented_html(duration)
    server = _BenchServer(("127.0.0.1", 0), _handler_type(game, html, box))
    thread = threading.Thread(target=server.serve_forever, name="chonoi-bench-http", daemon=True)
    process = None
    profile = None

    def stop_browser():
        nonlocal process, profile
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        process = None
        if profile is not None:
            profile.cleanup()
            profile = None

    def launch(width, height):
        nonlocal process, profile
        profile = tempfile.TemporaryDirectory(prefix="chonoi-bench-browser-", ignore_cleanup_errors=True)
        url = f"http://127.0.0.1:{server.server_address[1]}/"
        process = subprocess.Popen(browser_command(browser, profile.name, url, width, height),
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        game.start()
        thread.start()
        launch(WIDTH, HEIGHT)
        if not box.viewport_ready.wait(5):
            raise RuntimeError("trình duyệt không báo viewport")
        if box.viewport != [WIDTH, HEIGHT]:
            outer_width = WIDTH + (WIDTH - box.viewport[0])
            outer_height = HEIGHT + (HEIGHT - box.viewport[1])
            stop_browser()
            box.viewport = None
            box.viewport_ready.clear()
            launch(outer_width, outer_height)
            if not box.viewport_ready.wait(5):
                raise RuntimeError("trình duyệt không báo viewport sau hiệu chỉnh")
            if box.viewport != [WIDTH, HEIGHT]:
                raise RuntimeError(f"không hiệu chỉnh được viewport 1280x720: nhận {box.viewport!r}")
        timeout = WARMUP_S + duration + 15.0
        if not box.ready.wait(timeout):
            if process.poll() is not None:
                raise RuntimeError(f"trình duyệt dừng sớm với mã {process.returncode}")
            raise RuntimeError("benchmark quá thời gian chờ")
        if box.error:
            raise RuntimeError(box.error)
        _write_json_atomic(out_path, box.value)
        return box.value
    finally:
        stop_browser()
        server.shutdown()
        server.server_close()
        if thread.is_alive():
            thread.join(timeout=2)
        game.stop()


def main(argv=None):
    parser = _Parser(prog="chonoi.bench")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--duration", required=True, type=_positive_duration, help="số giây đo sau 3 giây làm nóng")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        result = run_benchmark(args.seed, args.duration, args.out)
    except (OSError, RuntimeError) as exc:
        sys.stderr.write(f"benchmark lỗi: {exc}\n")
        return 1
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
