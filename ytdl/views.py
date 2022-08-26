from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
import youtube_dl
from .forms import DownloadForm
import re
E='?'
D='shorts/'

def download_video(request):
    global context
    form = DownloadForm(request.POST or None)

    if form.is_valid():
        video_url = form.cleaned_data.get("url")
        Z = r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+'
        if not re.match(Z,video_url):
            return HttpResponse('Enter correct url.')
        if D in video_url:video_url='https://youtube.com/watch?v='+video_url.split(D)[1].split(E)[0]+E
        ydl_opts = {}
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(
                    video_url, download=False)
            video_audio_streams = []
            for m in meta['formats']:
                file_size = m['filesize']
                if file_size is not None:
                    file_size = f'{round(int(file_size) / 1000000,2)} mb'

                resolution = 'Audio'
                if m['height'] is not None:
                    resolution = f"{m['height']}x{m['width']}"
                video_audio_streams.append({
                    'resolution': resolution,
                    'extension': m['ext'],
                    'file_size': file_size,
                    'video_url': m['url']
                })
            video_audio_streams = video_audio_streams[::-1]
            A=0
            B='extension'
            for C in video_audio_streams:C[B] = C[B]+('(only audio)' if C['resolution']=='Audio' else('(video+audio)'if A==0 or A==1 else '(only video)'));A+=1
            context = {
                'form': form,
                'title': meta.get('title', None),
                'streams': video_audio_streams,
                'description': meta.get('description'),
                'likes': f'{int(meta.get("like_count", 0)):,}',
                'dislikes': f'{int(meta.get("dislike_count", 0)):,}',
                'thumb': meta.get('thumbnails')[len(meta.get('thumbnails'))-1]['url'],
                'duration': round(int(meta.get('duration', 1))/60, 2),
                'views': f'{int(meta.get("view_count")):,}'
            }
            return render(request, 'index.html', context)
        except Exception as error:
            return HttpResponse(error.args[0])
    return render(request, 'index.html', {'form': form})
