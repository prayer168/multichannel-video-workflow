import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "youtube-publish/scripts/preflight.py"
spec = importlib.util.spec_from_file_location("publish_preflight", SCRIPT)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class PublishScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "copy.txt").write_text(
            "【YouTube 標題】\nExample\n【說明欄】\nReady to publish.\n",
            encoding="utf-8",
        )
        self.manifest = {
            "batch_id": "test",
            "channel": {"youtube_channel_id": "UC" + "a" * 22},
            "visibility": "public",
            "items": [],
        }

    def item(self, key, kind):
        video = self.root / (key + ".mp4")
        video.write_bytes(key.encode())
        return {
            "id": key, "kind": kind, "video": video.name, "copy": "copy.txt",
            "made_for_kids": False, "altered_content": False,
            "related_to": "long", "subtitles": [],
        }

    def inspect(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        return preflight.inspect(path)

    def test_single_main(self):
        self.manifest["items"] = [self.item("long", "long")]
        self.assertTrue(self.inspect()["ok"])

    def test_standard_batch(self):
        self.manifest["items"] = [self.item("long", "long")] + [
            self.item(f"short-{i}", "short") for i in range(3)
        ]
        self.assertTrue(self.inspect()["ok"])

    def test_shorts_only_use_existing_main_and_ignore_excluded_files(self):
        self.manifest["items"] = [
            {"id": "long", "kind": "long", "video": "missing.mp4"},
            self.item("short-1", "short"),
        ]
        self.manifest["upload_scope"] = ["short-1"]
        self.manifest["existing_long_video"] = {"video_id": "UXexkZEIJLY"}
        result = self.inspect()
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual([i["id"] for i in result["items"]], ["short-1"])

    def test_excluded_main_requires_existing_video(self):
        self.manifest["items"] = [
            self.item("long", "long"), self.item("short-1", "short")
        ]
        self.manifest["upload_scope"] = ["short-1"]
        self.assertFalse(self.inspect()["ok"])

    def test_invalid_scopes(self):
        self.manifest["items"] = [self.item("long", "long")]
        for scope in ([], ["missing"], ["long", "long"], "long", [{}]):
            with self.subTest(scope=scope):
                self.manifest["upload_scope"] = scope
                with self.assertRaises(ValueError):
                    self.inspect()

    def test_invalid_kind_and_empty_batch(self):
        self.assertFalse(self.inspect()["ok"])
        self.manifest["items"] = [self.item("video", "unsupported")]
        self.assertFalse(self.inspect()["ok"])

    def test_invalid_existing_video_and_duplicate_bytes(self):
        self.manifest["items"] = [self.item("short-1", "short")]
        self.manifest["existing_long_video"] = {"video_id": "bad"}
        self.assertFalse(self.inspect()["ok"])
        self.manifest["items"] = [self.item("long", "long"), self.item("other", "long")]
        self.manifest.pop("existing_long_video")
        (self.root / "other.mp4").write_bytes(b"long")
        self.assertFalse(self.inspect()["ok"])


if __name__ == "__main__":
    unittest.main()
