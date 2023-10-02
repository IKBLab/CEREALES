import sys
import re
from collections import Counter

def get_speakers(lines, pattern):
    speakers_candidates = Counter()

    for i, line in enumerate(lines):
        match = pattern.fullmatch(line)

        if match:
            content = match.group(2)
            # detecting speaker candidate
            if content[-2:] == " :":
                speakers_candidates.update([content[:-2]])

            # detect the end of the transcription
            if "----------" in line and "FIN DE L’ENREGISTREMENT" in lines[i + 2]:
                break

    print("Speakers:", speakers_candidates.most_common())

    speakers_selection = set()
    for speaker_candidate, count in speakers_candidates.items():
        if count < 3:
            print("/!\\ Warning: speaker candidate \"%s\" is discarded (count = %i)"%(speaker_candidate, count))
        else:
            speakers_selection.add(speaker_candidate)

    return speakers_selection

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        print("Processing file", filename)

        if filename[-4:] != ".txt":
            print("Error: this file (%s) is not a txt file"%filename)
            print()
            continue

        pattern = re.compile("^([0-9]+)\s+(.+)$")

        with open(filename.replace(".txt", "_cleaned.txt"), "w") as output_file:
            with open(filename, "r") as input_file:
                data = input_file.read()
                lines = data.split('\n')

                beginning = True
                counter = 1

                speakers = get_speakers(lines, pattern)

                for i, line in enumerate(lines):
                    match = pattern.fullmatch(line)

                    if match:
                        line_number = int(match.group(1))

                        if beginning:
                            if line_number != 1:
                                # clean the useless infos at the beginning
                                continue
                            else:
                                beginning = False
                        else:
                            if line_number != counter:
                                print("Warning: line number (%i) doest not correspond with line count (%i) ; file line = %i"%(line_number, counter, i))
                                counter = line_number

                        # detect the end of the transcription
                        if "----------" in line and "FIN DE L’ENREGISTREMENT" in lines[i+2]:
                            break

                        content = match.group(2)

                        if content[:-2] in speakers:
                            output_file.write("\n" + content + " ")
                        else:
                            output_file.write(content + " ")
                        
                        counter += 1

                        if counter == 26:
                            counter = 1

        print("Processing: DONE")