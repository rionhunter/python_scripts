import os
import tempfile
import wave
import unittest

from utils.audio_utils.audio_speed_change import speed_change_command
from utils.audio_utils.audio_fade import fade_command
from utils.audio_utils.audio_reverse import reverse_command
from utils.audio_utils.audio_overlay import overlay_command
from utils.audio_utils.audio_split import split_command
from utils.audio_utils.extract_channels import channel_command
from utils.audio_utils.trim_silence import trim_silence_command
from utils.audio_utils.audio_join import join_command
from utils.audio_utils.audio_loop import loop_command
from utils.audio_utils.audio_to_mono import to_mono_command
from utils.audio_utils.audio_normalize_ffmpeg import normalize_command
from utils.audio_utils.audio_sample_rate import sample_rate_command
from utils.audio_utils.audio_metadata import get_wav_metadata
from utils.audio_utils.record_microphone import record_command
from utils.audio_utils.drag_convert_gui import convert_to_mp3


class TestAudioUtils(unittest.TestCase):
    def test_speed_change_command(self):
        self.assertEqual(
            speed_change_command('in.wav', 'out.wav', 1.5),
            ['ffmpeg', '-i', 'in.wav', '-filter:a', 'atempo=1.5', 'out.wav']
        )

    def test_fade_command(self):
        cmd = fade_command('in.wav', 'out.wav', 1, 4)
        self.assertIn('afade=t=in:st=0:d=1,afade=t=out:st=4:d=1', cmd)

    def test_reverse_command(self):
        self.assertEqual(
            reverse_command('in.wav', 'out.wav'),
            ['ffmpeg', '-i', 'in.wav', '-filter:a', 'areverse', 'out.wav']
        )

    def test_overlay_command(self):
        cmd = overlay_command('a.wav', 'b.wav', 'out.wav')
        self.assertIn('amix=inputs=2:duration=first:dropout_transition=2', cmd)

    def test_split_command(self):
        self.assertEqual(
            split_command('in.wav', 5, 10, 'out.wav'),
            ['ffmpeg', '-ss', '5', '-t', '10', '-i', 'in.wav', 'out.wav']
        )

    def test_channel_command(self):
        cmd = channel_command('in.wav', 1, 'right.wav')
        self.assertIn('FR', ' '.join(cmd))

    def test_trim_silence_command(self):
        cmd = trim_silence_command('in.wav', 'out.wav')
        self.assertIn('silenceremove', ' '.join(cmd))

    def test_join_command(self):
        cmd = join_command(['a.wav', 'b.wav'], 'out.wav')
        self.assertEqual(cmd.count('-i'), 2)
        self.assertEqual(cmd[-1], 'out.wav')

    def test_loop_command(self):
        self.assertEqual(
            loop_command('in.wav', 'out.wav', 3),
            ['ffmpeg', '-stream_loop', '2', '-i', 'in.wav', '-c', 'copy', 'out.wav']
        )

    def test_to_mono_command(self):
        self.assertEqual(
            to_mono_command('in.wav', 'out.wav'),
            ['ffmpeg', '-i', 'in.wav', '-ac', '1', 'out.wav']
        )

    def test_normalize_command(self):
        self.assertEqual(
            normalize_command('in.wav', 'out.wav'),
            ['ffmpeg', '-i', 'in.wav', '-filter:a', 'loudnorm', 'out.wav']
        )

    def test_sample_rate_command(self):
        self.assertEqual(
            sample_rate_command('in.wav', 'out.wav', 22050),
            ['ffmpeg', '-i', 'in.wav', '-ar', '22050', 'out.wav']
        )

    def test_get_wav_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'test.wav')
            with wave.open(path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes(b'\x00\x00' * 44100)
            ch, rate, dur = get_wav_metadata(path)
            self.assertEqual(ch, 1)
            self.assertEqual(rate, 44100)
            self.assertAlmostEqual(dur, 1.0, places=2)

    def test_record_command(self):
        self.assertEqual(
            record_command('out.wav', 5),
            ['ffmpeg', '-f', 'alsa', '-i', 'default', '-t', '5', 'out.wav']
        )

    def test_convert_to_mp3(self):
        self.assertEqual(
            convert_to_mp3('audio.ogg'),
            ['ffmpeg', '-i', 'audio.ogg', 'audio.mp3']
        )


if __name__ == '__main__':
    unittest.main()
