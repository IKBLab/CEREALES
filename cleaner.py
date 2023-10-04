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
    for file in sys.argv[1:]:
        print("Processing file", file)
        filename, extension = file.split('.')

        if extension != "txt":
            print("Error: this file (%s) is not a txt file"%file)
            print()
            continue

        pattern = re.compile("^([0-9]+)\s+(.+)$")

        with open(filename + "_cleaned.tmp", "w") as output_file:
            with open(file, "r") as input_file:
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
                                print("INFO : line number (%i) does not correspond with line count (%i) ; file line = %i"%(line_number, counter, i))
                                counter = line_number
    
                        # detect the end of the transcription
                        #if "----------" in line and "FIN DE L’ENREGISTREMENT" in lines[i+2]:
                        #    break

                        content = match.group(2)

                        if content[:-2] in speakers:
                            output_file.write("\n" + content + " ")
                        else:
                            output_file.write(content + " ")

                        counter += 1

                        if counter == 26:
                            counter = 1

        # once we created one big cleaned file, we divide it into smaller chunks, each corresponding to a different audio file
        with open(filename + "_cleaned.tmp") as big_file:
            data = big_file.read()
            lines = data.split('\n')

            if lines[0].strip() == "OUVERTURE DE L’AUDIENCE":
                del lines[0]
                print("OK : removing first line")
            else:
                print("WARNING : first line not found")

            count_output_files = 1
            output_file = open(filename + "_cleaned_%i.txt"%count_output_files, "w")
            speakers_in_file = set()

            for line in lines:
                # sanity check
                assert " : " in line
                speakers_in_file.add(line.split(' : ')[0])

                if "--" in line:
                    if "SUSPENSION" in line or "REPRISE" in line:
                        # sanity checks
                        assert "SUSPENSION ---------- REPRISE" in line
                        s = line.split("SUSPENSION ---------- REPRISE")
                        assert len(s) == 2 and len(s[1].strip()) == 0

                        output_file.write(s[0])
                        output_file.close() # we change of file
                        print("Found %i speakers in this file:"%len(speakers_in_file), speakers_in_file)
                        speakers_in_file = set()
                        print("Changing file!")

                        count_output_files += 1
                        output_file = open(filename + "_cleaned_%i.txt" % count_output_files, "w")
                    else:
                        # sanity check
                        assert line.count("----------") >= 2

                        # this case occurs when extra information was included in the original transcription
                        # we discard the extra information
                        output_file.write(line.split("----------")[0] + '\n')
                else:
                    output_file.write(line + '\n')


            output_file.close()
            print("Found %i speakers in this file:" % len(speakers_in_file), speakers_in_file)
        print("Processing: DONE")