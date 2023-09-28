import requests
import os
import urllib3
import subprocess

from tqdm import tqdm
from bs4 import BeautifulSoup
from pydub import AudioSegment

path = "dataset"

base_url = "https://www.cerp.gouv.qc.ca/"
base_page = "index.php?id=56&no_cache=1&L=920"

url = base_url+base_page

try:
    os.mkdir(path)
except:
    pass


def download(url, path):
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)

    with open(path, 'wb') as out:
        while True:
            data = r.read(8192)
            if not data:
                break
            out.write(data)

    r.release_conn()


def get_length(filepath):
    complete_audio = AudioSegment.from_file(filepath)

    return complete_audio.__len__()/1000

def convert_video_to_audio_ffmpeg(video_path, audio_path):
    command = f"ffmpeg -i '{video_path}' -ac 1 -ar 16k '{audio_path}'"

    subprocess.call(command, shell=True,         
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

r = requests.get(url)

main_soup = BeautifulSoup(r.content, 'html.parser')

audiences = {}
total_length = 0

for audiences_container in main_soup.findAll("ul", {"class": "audiences-outils"}):
    links = []

    # get links
    for link in audiences_container.findAll("a"):
        links.append(link.get('href'))
    
    # get audience date
    for audience_date in audiences_container.find("span"):
        date = audience_date.get_text().strip()

    # Dont register if there isn't two links (video + transcription)
    if len(links) == 2:
        audiences[date] = links


for key in tqdm(audiences.keys()):
    audience_path = path+"/"+key
    try:
        os.mkdir(audience_path)
    except:
        pass

    # Download transcript
    download(base_url+audiences[key][1], audience_path+f"/transcription.pdf")

    # Handle videos
    audience_page = requests.get(base_url+audiences[key][0])
    audience_soup = BeautifulSoup(audience_page.content, 'html.parser')
    for audiences_container in audience_soup.findAll("ul", {"class": "audiences-video-parties"}):
        count = 0
        for audiences_link in audiences_container.findAll("a"):
            count+=1
            video_page = requests.get(base_url+"/"+audiences_link.get("href"))
            video_soup = BeautifulSoup(video_page.content, 'html.parser')
            video_url = video_soup.find('video').find('source').get("src")

            video_path = audience_path+f"/video_{count}.mp4"
            audio_path = audience_path+f"/audio_{count}.wav"
            if not os.path.isfile(audio_path):
                if not os.path.isfile(video_path):
                    download(video_url, video_path)
                convert_video_to_audio_ffmpeg(video_path, audio_path) 
                os.remove(video_path)
            else:
                print(f"[{audio_path} exists] skipping...")

            total_length+= get_length(audio_path)

print(f"total length = {total_length}s ({total_length/60}mins) with {len(audiences.keys())} videos")