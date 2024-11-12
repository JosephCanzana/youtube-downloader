from pytubefix import YouTube


yt = YouTube('https://youtu.be/dQw4w9WgXcQ?si=dKMIypGK_maFXuG5')

print(yt.title)
#yt.streams.get_highest_resolution().download()
