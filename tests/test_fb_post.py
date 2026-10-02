"""CLI regression coverage for channel isolation and optional English copy."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'fb_post.py'


class FacebookPostTests(unittest.TestCase):
    def run_cli(self, project, *args):
        subprocess.run([sys.executable, str(SCRIPT), str(project), *args],
                       check=True, capture_output=True, encoding='utf-8')

    def test_channel_isolation_without_english(self):
        for channel, expected in [('ai-watch', 'AI 觀測站（AI Watch）'),
                                  ('blackbear-science', '黑熊老師的自然教室'),
                                  (None, '影片宣傳')]:
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                folder = project / '3_製作後' / '臉書宣傳'
                folder.mkdir(parents=True)
                original = '月相 <觀察> & 記錄 【YouTube 連結】'
                source = folder / '臉書文_中文.txt'
                source.write_text(original, encoding='utf-8')
                args = ['--channel', channel] if channel else []
                self.run_cli(project, *args)
                page = (folder / 'facebook-post.html').read_text(encoding='utf-8')
                self.assertIn(expected + ' ·', page)
                self.assertIn('&lt;觀察&gt; &amp;', page)
                if channel != 'blackbear-science':
                    self.assertNotIn('黑熊老師', page)
                self.run_cli(project, *args, '--url', 'https://youtu.be/example')
                self.assertEqual(source.read_text(encoding='utf-8'), original)
                self.assertIn('https://youtu.be/example',
                              (folder / '臉書文_中文_含連結.txt').read_text(encoding='utf-8'))
                self.assertFalse((folder / '臉書文_英文_含連結.txt').exists())
                updated = (folder / 'facebook-post.html').read_text(encoding='utf-8')
                self.assertIn(expected + ' ·', updated)

    def test_bilingual_reruns_preserve_originals_and_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            folder = project / '3_製作後' / '臉書宣傳'
            folder.mkdir(parents=True)
            (folder / '臉書文_中文.txt').write_text('觀看【YouTube 連結】', encoding='utf-8')
            source = folder / '臉書文_英文.txt'
            source.write_text('Watch [YouTube link]', encoding='utf-8')
            for _ in range(2):
                self.run_cli(project, '--channel', 'ai-watch', '--url', 'https://youtu.be/example')
            self.assertEqual(source.read_text(encoding='utf-8'), 'Watch [YouTube link]')
            for suffix in ['', '_2']:
                exported = folder / f'臉書文_英文_含連結{suffix}.txt'
                self.assertEqual(exported.read_text(encoding='utf-8').strip(), 'Watch https://youtu.be/example')
            self.assertNotIn('黑熊老師', (folder / 'facebook-post.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
