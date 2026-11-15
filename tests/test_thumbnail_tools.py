import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "youtube-thumbnail-strategist"
spec = importlib.util.spec_from_file_location("validate_manifest", SKILL / "scripts/validate_manifest.py")
validate_manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_manifest)
EXAMPLE = json.loads((SKILL / "assets/manifest-example.json").read_text(encoding="utf-8"))


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / "製作後" / "縮圖候選"
        self.dir.mkdir(parents=True)

    def errors(self, manifest):
        path = self.dir / "thumbnail_manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        return validate_manifest.validate(path)

    def test_example_is_valid(self):
        self.assertEqual(self.errors(EXAMPLE), [])

    def test_generator_must_be_codex_images(self):
        manifest = copy.deepcopy(EXAMPLE)
        manifest["generator"] = {"agent": "local", "model": "ffmpeg"}
        self.assertIn("generator must be Codex / Images 2.6", self.errors(manifest))

    def test_short_accepts_single_candidate(self):
        manifest = copy.deepcopy(EXAMPLE)
        manifest["video_kind"] = "short"
        manifest["candidates"] = manifest["candidates"][:1]
        self.assertEqual(self.errors(manifest), [])

    def test_long_needs_three_candidates(self):
        manifest = copy.deepcopy(EXAMPLE)
        manifest["candidates"] = manifest["candidates"][:1]
        self.assertIn("long needs exactly 3 candidates A, B, C", self.errors(manifest))

    def test_approved_requires_passing_facebook_image(self):
        manifest = copy.deepcopy(EXAMPLE)
        (self.dir / "thumbnail_A.png").write_bytes(b"png")
        manifest["status"] = "approved"
        manifest["candidates"][0].update(image_file="thumbnail_A.png", qa_status="pass", attempts=1)
        errors = self.errors(manifest)
        self.assertIn("facebook_image must exist and pass QA for qa_passed+", errors)
        fb_dir = self.dir.parent / "臉書宣傳"
        fb_dir.mkdir()
        (fb_dir / "臉書分享圖_1200x630.png").write_bytes(b"png")
        manifest["facebook_image"].update(file="../臉書宣傳/臉書分享圖_1200x630.png", qa_status="pass", attempts=1)
        self.assertEqual(self.errors(manifest), [])

    def test_short_facebook_image_must_be_vertical_name(self):
        manifest = copy.deepcopy(EXAMPLE)
        manifest["video_kind"] = "short"
        manifest["candidates"] = manifest["candidates"][:1]
        fb_dir = self.dir.parent / "臉書宣傳"
        fb_dir.mkdir()
        (fb_dir / "臉書分享圖_1200x630.png").write_bytes(b"png")
        manifest["facebook_image"]["file"] = "../臉書宣傳/臉書分享圖_1200x630.png"
        self.assertIn("facebook_image: short file name must contain 1080x1350", self.errors(manifest))


try:
    from PIL import Image
except ImportError:
    Image = None


@unittest.skipIf(Image is None, "Pillow not installed")
class InspectImagesTests(unittest.TestCase):
    def run_inspect(self, folder):
        return subprocess.run([sys.executable, str(SKILL / "scripts/inspect_images.py"), str(folder)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_all_eight_image_kinds_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            Image.new("RGB", (1280, 720)).save(root / "thumbnail_A.png")
            Image.new("RGB", (1280, 720)).save(root / "縮圖.jpg", "JPEG")
            Image.new("RGB", (1080, 1920)).save(root / "shorts_cover.png")
            Image.new("RGB", (1200, 630)).save(root / "臉書分享圖_1200x630.png")
            Image.new("RGB", (1080, 1350)).save(root / "臉書分享圖_1080x1350.png")
            Image.new("RGB", (640, 360)).save(root / "ref_A_83s.jpg")
            result = self.run_inspect(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("PASS: 5 image(s)", result.stdout)

    def test_wrong_facebook_size_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            Image.new("RGB", (1080, 1080)).save(root / "臉書分享圖_1080x1350.png")
            result = self.run_inspect(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("expected 1080x1350", result.stdout)


if __name__ == "__main__":
    unittest.main()
