from plugin import plugin
import youtube_dl
import urllib.request
import requests
import urllib.parse

@require(network = True)
@plugin("mp3download")
def mp3download(jarvis):

    jarvis.say("Enter the name of the music")
    query = jarvis.input()
    query_string = urllib.parse.urlencode({"search_query" : "{}".format(query)})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    url = "http://www.youtube.com/watch?v=" + search_results[0]

    ydl_opts = {

        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors' : [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
        }],
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["{}".format(url)])
        res = ydl.extract_info("{}".format(url))
        filename = ydl.prepare_filename(res)
