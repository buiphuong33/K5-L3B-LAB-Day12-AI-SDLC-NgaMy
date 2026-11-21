"""Kiểm tra đầu ra headless tất định cho cả hai mode của contract."""

import os
import unittest

from helpers import Workdir, run_headless


class Determinism(unittest.TestCase):
    def test_same_seed_produces_identical_bytes_in_every_mode(self):
        for mode in ("gather", "quan"):
            with self.subTest(mode=mode), Workdir() as w:
                outputs = [w.path("first.jsonl"), w.path("second.jsonl")]
                for output in outputs:
                    code, err = run_headless(
                        "--mode", mode,
                        "--seed", "202604077",
                        "--ticks", "180",
                        "--snapshot-every", "30",
                        "--out", output,
                    )
                    self.assertEqual(code, 0, err)

                with open(outputs[0], "rb") as first, open(outputs[1], "rb") as second:
                    self.assertEqual(
                        first.read(),
                        second.read(),
                        f"{mode} phải cho đầu ra giống từng byte khi dùng cùng seed",
                    )

                self.assertGreater(os.path.getsize(outputs[0]), 0)


if __name__ == "__main__":
    unittest.main()
