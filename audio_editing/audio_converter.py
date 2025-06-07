from pydub import AudioSegment
import argparse

parser = argparse.ArgumentParser(description="Convert an audio file to another format.")
parser.add_argument("input_file", help="Source audio")
parser.add_argument("output_file", help="Converted audio path with extension")
args = parser.parse_args()

audio = AudioSegment.from_file(args.input_file)
audio.export(args.output_file, format=args.output_file.split('.')[-1])

