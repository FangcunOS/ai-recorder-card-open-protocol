#!/usr/bin/env python3
import importlib.util
import sys
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "qs668_transcribe",
    Path(__file__).with_name("qs668-transcribe.py"),
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class TranscribeHelperTests(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(MOD.format_timestamp(65), "01:05")
        self.assertEqual(MOD.format_timestamp(3661), "01:01:01")
        self.assertEqual(MOD.format_timestamp_ms(4300), "00:04")

    def test_plan_chunks_merges_tiny_tail(self):
        plans = MOD.plan_chunks(500, 480)
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0].end_s, 500)

    def test_plan_chunks_splits_long_audio(self):
        plans = MOD.plan_chunks(1200, 480)
        self.assertEqual(len(plans), 3)
        self.assertEqual(plans[-1].end_s, 1200)

    def test_utterances_and_merge(self):
        lines = MOD.utterances_to_lines(
            [{"text": "你好", "start_time": 0, "end_time": 1200}],
            offset_s=60,
        )
        self.assertEqual(lines, ["[01:00] 你好"])
        result = MOD.ChunkResult(MOD.ChunkPlan(0, 60, 70), "你好", lines)
        text, has_timeline = MOD.merge_transcript([result])
        self.assertTrue(has_timeline)
        self.assertEqual(text, "[01:00] 你好")

    def test_explain_doubao_error(self):
        text = MOD.explain_doubao_error("45000001", "unauthorized", 401)
        self.assertIn("鉴权失败", text)
        quota = MOD.explain_doubao_error("", "资源包时长不足", 400)
        self.assertIn("额度不足", quota)

    def test_write_corpus_front_matter(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "demo.wav"
            audio.write_bytes(b"RIFF")
            path = MOD.write_corpus(
                audio,
                "[00:00] 你好",
                Path(tmp),
                "zh",
                1,
                5.0,
                "doubao",
                True,
                title="拜访纪要",
                customer="客户A",
                sync_status="local",
            )
            body = path.read_text(encoding="utf-8")
            self.assertIn("title: \"拜访纪要\"", body)
            self.assertIn("customer: \"客户A\"", body)
            self.assertIn("sync_status: \"local\"", body)
            self.assertIn("## Transcript", body)


if __name__ == "__main__":
    unittest.main()
