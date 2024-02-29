import sys
from yt_dlp import YoutubeDL
if len(sys.argv) < 2:
    print('Usage: yt.py <url>')
    sys.exit(1)
with YoutubeDL() as ydl:
    ydl.download([sys.argv[1]])
