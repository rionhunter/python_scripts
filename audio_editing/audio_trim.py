from pydub import AudioSegment
import argparse

parser = argparse.ArgumentParser(description="Trim an audio file to a start and end time in seconds.")
parser.add_argument("input_file", help="Path to the source audio file")
parser.add_argument("start", type=float, help="Start time in seconds")
parser.add_argument("end", type=float, help="End time in seconds")
parser.add_argument("output_file", help="Where to save the trimmed audio")
args = parser.parse_args()

audio = AudioSegment.from_file(args.input_file)
trimmed = audio[args.start * 1000: args.end * 1000]
trimmed.export(args.output_file, format=args.output_file.split('.')[-1])

