from pytube import YouTube
from sys import argv

link = argv[1]
yt = YouTube(link)

print(f"Title {yt.title}")