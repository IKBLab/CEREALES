# Commission_Viens_Dataset
Scraper and cleaner for the Commission Viens (https://www.cerp.gouv.qc.ca/index.php?id=56&amp;no_cache=1)

## Installation

```bash
python -m virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Scraper

```bash
python scraper.py
```

## Align_from_textgrid
Use the Montreal Forced Aligner to align audio with text (only one file):
```bash
mfa align_one audiofile.wav audiotext_to_align.txt french_mfa french_mfa test --use_mp --beam 100 --retry_beam 400
```
to align a folder:
```bash
mfa align corpus/path/ french_mfa french_mfa output/path --use_mp --beam 10000 --retry_beam 40000
```

(`beam` and `retry_beam` must be adjusted according to the duration of the audio file.)

for aligning only one file
```bash
python read_mfa.py --text_file input/path/filename.txt --textgrid_file input/path/filename.TextGrid --output_path output/corpus
```

for aligning file pairs from a folder (filename.txt, filename.TexGrid)
```bash
python align_from_textgrid --folder input/path/ --output_path output/corpus
```

## generate_segments_from_json

```bash
python generate_segments_from_json.py file 
```
