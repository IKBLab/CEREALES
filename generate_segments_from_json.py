import sys
import os
import re
import json
from scipy.io import wavfile

if __name__ == "__main__":
    for file in sys.argv[1:]:
        print("Processing file", file)
        filename, extension = file.split('.')

        if extension != "json":
            print("Error: this file (%s) is not a json file"%file)
            print()
            continue

        rate, audiodata = wavfile.read(filename + ".wav")
        assert rate == 16000

        os.makedirs("./%s_segments_aeneas"%filename, exist_ok=True)

        with open(file, "r") as input_file:
            data = json.load(input_file)['fragments']

            for frag in data:
                begin = int(float(frag['begin']) * rate)
                end = int(float(frag['end']) * rate)

                sub_array = audiodata[begin:end]

                wavfile.write("./%s_segments_aeneas/%s.wav"%(filename, frag['id']), rate, sub_array)

        print("Processing: DONE")