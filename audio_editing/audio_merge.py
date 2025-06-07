from pydub import AudioSegment
import argparse

parser = argparse.ArgumentParser(description="Merge multiple audio files into one.")
parser.add_argument("input_files", nargs='+', help="List of audio files to merge")
parser.add_argument("output_file", help="Path for merged audio")
args = parser.parse_args()

combined = AudioSegment.empty()
for path in args.input_files:
    combined += AudioSegment.from_file(path)
combined.export(args.output_file, format=args.output_file.split('.')[-1])

