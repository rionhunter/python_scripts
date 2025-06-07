from pydub import AudioSegment
import argparse

parser = argparse.ArgumentParser(description="Normalize an audio file to a target dBFS level.")
parser.add_argument("input_file", help="Audio file to normalize")
parser.add_argument("output_file", help="Path for the normalized audio")
parser.add_argument("--target-dBFS", type=float, default=-20.0, dest="target", help="Target loudness in dBFS")
args = parser.parse_args()

audio = AudioSegment.from_file(args.input_file)
change_in_dBFS = args.target - audio.dBFS
normalized = audio.apply_gain(change_in_dBFS)
normalized.export(args.output_file, format=args.output_file.split('.')[-1])

