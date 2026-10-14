import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import avatar_kit


class AvatarKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.image = self.root / 'portrait.png'
        self.image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'abc123')
        self.audio = self.root / 'speech.wav'
        self.audio.write_bytes(b'RIFF\x04\x00\x00\x00WAVE' + b'abcdef')
        self.comfy = self.root / 'ComfyUI'
        (self.comfy / 'input').mkdir(parents=True)
        self.workflow = self.root / 'api.json'
        self.workflow.write_text(json.dumps({
            '12': {'class_type': 'LoadImage', 'inputs': {'image': 'before.png'}},
            '14': {'class_type': 'LoadAudio', 'inputs': {'audio': 'before.wav'}},
            '20': {'class_type': 'SaveVideo', 'inputs': {'other': ['12', 0]}},
        }), encoding='utf-8')

    def test_valid_headers(self):
        self.assertEqual(avatar_kit.verify_file(self.image, 'image'), self.image)
        self.assertEqual(avatar_kit.verify_file(self.audio, 'audio'), self.audio)
        self.audio.write_bytes(b'not audio')
        with self.assertRaises(avatar_kit.AvatarKitError):
            avatar_kit.verify_file(self.audio, 'audio')

    def test_reject_ui_workflow(self):
        self.workflow.write_text('{"nodes": []}', encoding='utf-8')
        with self.assertRaises(avatar_kit.AvatarKitError):
            avatar_kit.load_api_workflow(self.workflow)

    def test_stage_and_patch(self):
        filename = avatar_kit.stage_file(self.image, self.comfy / 'input', 'image')
        self.assertTrue((self.comfy / 'input' / filename).exists())
        graph = avatar_kit.load_api_workflow(self.workflow)
        avatar_kit.apply_media(graph, '12', 'image', filename)
        self.assertEqual(graph['12']['inputs']['image'], filename)
        with self.assertRaises(avatar_kit.AvatarKitError):
            avatar_kit.apply_media(graph, '12', 'missing', filename)

    def test_only_loopback(self):
        self.assertEqual(avatar_kit.local_api_base('http://127.0.0.1:8188/'), 'http://127.0.0.1:8188')
        for url in ('https://127.0.0.1:8188', 'http://example.com:8188', 'http://127.0.0.1:8188/?foo=bar'):
            with self.assertRaises(avatar_kit.AvatarKitError):
                avatar_kit.local_api_base(url)

    def test_queue_dry_run_no_network(self):
        parser = avatar_kit.make_parser()
        args = parser.parse_args([
            'queue', '--workflow', str(self.workflow), '--comfy-root', str(self.comfy),
            '--image', str(self.image), '--audio', str(self.audio),
            '--image-node', '12', '--audio-node', '14', '--dry-run',
        ])
        with patch.object(avatar_kit, 'request_json', side_effect=AssertionError('network called')):
            self.assertEqual(avatar_kit.run(args), 0)

    def test_queue_checks_second_audio_pair(self):
        parser = avatar_kit.make_parser()
        args = parser.parse_args([
            'queue', '--workflow', str(self.workflow), '--comfy-root', str(self.comfy),
            '--image', str(self.image), '--audio', str(self.audio),
            '--image-node', '12', '--audio-node', '14', '--audio2', str(self.audio),
        ])
        with self.assertRaises(avatar_kit.AvatarKitError):
            avatar_kit.run(args)


if __name__ == '__main__':
    unittest.main()
