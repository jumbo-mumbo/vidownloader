import os, io, sys
import yt_dlp

from .schemas import VideoData
from .utils import (
    time_format, 
    format_bytes, 
    format_resolution,
    check_thumbnail
    )


class VideoMetadata:
    def __init__(
        self,
        url: str,
        ):
        
        self.url = url
        self.path = os.getcwd()
        
        self.metadata = self.__initialize_metadata()
        self.qualities = self._get_qualities()
      
        self.title: str 
        self.resource: str 
        self.duration: str 
        self.thumbnail: str 
        self.quality: str 


    def __initialize_metadata(self):
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl: 
            meta = ydl.extract_info(self.url, download=False)
            self.resource = list(ydl._ies_instances.keys())[0]
            self.title = meta.get('title', meta)
            self.duration = time_format(meta.get('duration', meta))
            self.thumbnail = self._get_thumbnail(meta.get('thumbnails', meta))
            self.ydl = ydl
  

    def _get_thumbnail(self, thumbnails):
        for t in thumbnails[::-1]:
            url = t['url']
            if not url.endswith(".webp") \
                and check_thumbnail(url):
                    return url


    def _get_qualities(self):
        ydl = self.ydl
        
        meta = ydl.extract_info(self.url, download=False)
        formats = meta.get('formats', meta)
        #print(meta)

        quality_list = []
        size_list = [] # In case i wanted to add size

        for f in formats:
            resolution = format_resolution(f.get('resolution', None))
            size = f.get('filesize_approx', f.get('filesize', None))
            fps = f.get('fps', "25")
        
            if not fps: fps = "25"
            
            if resolution and int(resolution):
                if int(fps) < 20:
                    continue
                
                quality = f"{resolution}p {int(fps)}fps"

                if quality not in quality_list:
                    if size:
                        size = format_bytes(size)
                        size_list.append(f" ,{size}")
                    
                    quality_list.append(quality)

        return quality_list[::-1]


    
class VideoDownload:
    def __init__(
        self,
        url: str,
        user_id: int,
        meta: bool = False,
        video: bool = True,
        audio: bool = True,
        resolution: int = 720,
        fps: int = 25
        ):
        
        self.url = url
        self.user_id = user_id

        if not meta:
            self.path = os.getcwd()
            self.ydl = self._get_ydl(self.options)

            self.video = video
            self.audio = audio
            self.resolution = resolution
            self.fps = fps

        else:
            self.metadata = VideoMetadata(url=self.url)
            

    def _get_ydl(self, options: dict):
        options = self._get_options()
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl     


    def _get_options(self):
        media_path = "videos"
        yo = {'quiet': True}
        #yo.update({'math_filter': self.quality_filter,})
        
        if not self.video:
            media_path = "audios"
            yo.update({'postprocessors': [{  # Extract audio using ffmpeg
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                        }]})

        elif not self.audio:
            media_path = "muted_video"

        yo.update({
            'outtmpl': self.path + f"/media/{media_path}" + "/%(uploader)s/%(title)s.%(ext)s"
            })
        return yo         

    def quality_filter(self, info, *, incomplete):
        resolution = info.get('resolution')
        print(resolution)
        if resolution == self.resolution:
            return True


    def _parse_quality(self):
        quality = self.quality.strip()
        res_idx = quality.find("p")
        fps_idx = quality.find("f")
        
        self.resolution = int(quality[:res_idx])
        self.fps = int(quality[res_idx+1: fps_idx])


    def download(self):
        ydl = self.ydl
        ydl.download()
    

    def delete(self):
        pass



def get_video_data(video: VideoDownload):
    v = video
    data = VideoData(
        user_id = v.user_id,
        name = v.metadata.title,
        resource = v.metadata.resource,
        duration = v.metadata.duration,
        image_url = v.metadata.thumbnail,
        video_url = v.metadata.url,
        qualities = v.metadata.qualities
        )

    return data
    

