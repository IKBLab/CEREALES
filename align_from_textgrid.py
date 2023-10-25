import json 
import mytextgrid
import string
import argparse
import os

# Function to parse a TextGrid file and extract interval information
def parse_textgrid(textgrid_file):
    tg = mytextgrid.read_from_file(textgrid_file)

    textgrid = []
    # Iterate through tiers
    if tg[0].is_interval():
        for interval in tg[0]:
            # For interval tiers
            # Print Interval attributes
            if interval.text != "" and interval.text !="<eps>":
                textgrid.append((interval.text, float(interval.xmin), float(interval.xmax)))
    
    return textgrid

# Function to align sentences from a text file with TextGrid intervals
def align_sentences_with_textgrid(text_file, textgrid_file):
    textgrid_intervals = parse_textgrid(textgrid_file)

    # Read the text from the text file
    with open(text_file, 'r') as file:
        sentences = file.readlines()
    
    sentence_timestamps = []
    interval_index = 0  # To keep track of the current TextGrid interval

    for sentence in sentences:
        sentence_start, sentence_end = None, None

        sentence_normalized = sentence.lower().strip()  # Convert to lowercase and remove leading/trailing spaces
        sentence_normalized = ''.join(char for char in sentence_normalized if char not in (string.punctuation + '’'))  # Remove punctuation
                
        # Ensure the sentence is not an empty string
        if sentence:
            while interval_index < len(textgrid_intervals):
                text, start, end = textgrid_intervals[interval_index]

                # Prepare TextGrid text for matching
                text_normalized = text.lower().strip()  # Convert to lowercase and remove leading/trailing spaces
                text_normalized = ''.join(char for char in text_normalized if char not in (string.punctuation + '’'))  # Remove punctuation
                
                if text_normalized in sentence_normalized:
                    if sentence_start is None:
                        sentence_start = start
                    sentence_normalized = sentence_normalized.replace(text_normalized, '', 1).strip()
                    sentence_end = end
                else:
                    if sentence_start is not None:
                        break  # Sentence has been found
                interval_index += 1

            if sentence_start is not None and sentence_end is not None:
                sentence_timestamps.append((sentence, sentence_start, sentence_end))

    return sentence_timestamps


def generate_file_pairs(folder):
    text_files = []
    textgrid_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                text_files.append(os.path.join(root, file))
            elif file.endswith(".TextGrid"):
                textgrid_files.append(os.path.join(root, file))

    return text_files, textgrid_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="align sentences from text with a TextGrid file from MFA and save the result as JSON.")
    parser.add_argument("--text_file", type=str, help="Path to the text file")
    parser.add_argument("--textgrid_file", type=str, help="Path to the TextGrid file")
    parser.add_argument("--folder", type=str, help="Path to a folder with pairs filename.txt filename.TextGrid, take priority over text_file and textgrid_file", default=None)
    parser.add_argument("--output_path", type=str, default="audio.json", help="Path to save the output JSON file (default: audio.json), if folder give a folder path")

    args = parser.parse_args()


    if args.folder:
        folder_path = args.folder
        text_file_path, textgrid_file_path = generate_file_pairs(folder_path)
        output_path = [args.output_path + item.rsplit(".")[0].split("/")[-1] + ".json" for item in text_file_path]
        try:
            os.mkdir(args.output_path)
        except:
            pass
    else:
        text_file_path = [args.text_file]
        textgrid_file_path = [args.textgrid_file]
        output_path = [args.output_path]

    for i in range(len(text_file_path)):
        print(f"Processing {text_file_path[i]}")
        sentences_and_timestamps = align_sentences_with_textgrid(text_file_path[i], textgrid_file_path[i])

        data = {"fragments": []}
        id = 0
        # Print the aligned sentences and their timestamps
        for sentence, start_time, end_time in sentences_and_timestamps:
            data["fragments"].append({
                "id": id,
                "begin": float(start_time),
                "end": float(end_time),
                "lines": sentence,
            })
            id+=1

        with open(output_path[i], "w") as input_file:
            json.dump(data, input_file)