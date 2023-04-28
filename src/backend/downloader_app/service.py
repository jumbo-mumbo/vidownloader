import os
import yt_dlp

from uuid import uuid4
from .schemas import MediaData
from .utils import (
    time_format, 
    format_bytes, 
    get_resolution_height, 
    check_thumbnail
    )


class DMetadata:
    def __init__(self):
        self.title: str
        self.resource: str
        self.duration: str
        self.duration_seconds: int
        self.thumbnail: str
        self.qualities: list | None = None

    def initialize_metadata(
            self, 
            ydl: yt_dlp.YoutubeDL, 
            url: str, 
            quality: bool = False
            ):
        meta = ydl.extract_info(url, download=False)
        self.resource = list(ydl._ies_instances.keys())[0]  # Extract video source (Youtube, Vk, etc.)
        self.title = meta.get("title", meta)
        self.duration = time_format(meta.get("duration", meta))
        self.duration_seconds = meta.get("duration", meta)
        self.thumbnail = self._get_thumbnail(meta.get("thumbnails", meta))

        if not quality:
            self.qualities = self._get_qualities(meta)


    def _get_thumbnail(self, thumbnails):
        for t in thumbnails[::-1]:
            url = t["url"]
            if not url.endswith(".webp") and check_thumbnail(url):
                return url
            

    def _get_qualities(self, meta):
        formats = meta.get("formats", meta)

        quality_list = []
        # size_list = []  # In case i wanted to add size
        for f in formats:
            resolution = get_resolution_height(f.get("resolution", None))

            if self.resource.lower().startswith("tiktok"):  # if its tiktok
                resolution = str(f.get("height", None))

            size = f.get("filesize_approx", f.get("filesize", 0))
            size = format_bytes(size)

            fps = f.get("fps", 25)
            if not fps:
                fps = 25

            if resolution.isdecimal() and int(resolution) >= 144:
                # Size limitation not higher than 1.5gb + 500mb to audio space
                if size and size["size"] > 1.5 and size["label"] == "GiB":
                    continue

                quality = f"{resolution}p"
                if int(resolution) > 720 and int(fps) > 50:
                    quality += f"{int(fps)}fps"

                if quality not in quality_list:
                    quality_list.append(quality)

        return quality_list[::-1]


class Downloader(DMetadata):
    def __init__(
        self,
        url: str,
        user_id: int,
        quality: str | None = None,
    ):
        self.url = url
        self.user_id = user_id
       
        self.quality = quality
        self.file_key = uuid4()
        self.file_ext = "mp4"
        self.path = os.getcwd().removesuffix("/src/backend")

        self.ydl = self._get_ydl()
        
    def _get_ydl(self):
        ydl = yt_dlp.YoutubeDL

        if not self.quality:
            self.initialize_metadata(ydl({"quiet": True}), self.url)
        
        else:
            options = self._get_options()
            ydl = ydl(options)
            self.initialize_metadata(ydl, self.url, self.quality)

        return ydl

    def _get_options(self):
        yo = {"quiet": True, "no-part": True}

        # video format bad audio top
        if self.quality == "audio":
            yo.update(
                {
                    "postprocessors": [
                        {  # Extract audio using ffmpeg
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "m4a",
                        }
                    ]
                }
            )

        else:
            yo.update(
                {
                    "format": self.quality_filter,
                }
            )

        yo.update({"outtmpl": self.path + f"/media/" + f"{self.file_key}" + ".%(ext)s"})
        return yo

    # Take a video that fits certain quality
    def quality_filter(self, info):
        formats = reversed(info["formats"])
        # size = f.get('filesize_approx', f.get('filesize', None))

        fmt = {}
        for f in formats:
            if fmt.get("audio") and fmt.get("video"):
                break

            chosen_resolution, chosen_fps = self._parse_quality(self.quality)

            format_fps = f.get("fps", 25)  # Extracting fps
            format_media_marks = [  # Extracting resolution
                get_resolution_height(f.get("resolution")),
                f.get("format_note"),
                f.get("height"),
            ]

            media_type = self._get_media_type(  # Check for chosen resolution
                format_media_marks, chosen_resolution
            )

            if media_type:
                if media_type == "audio" and not fmt.get("audio"):
                    fmt.update({"audio": f})
                elif media_type == "video" and not fmt.get("video"):
                    dr = f["dynamic_range"]  # Extract dynamic range, and forbid hdr
                    if not dr.startswith("HDR") and f["video_ext"] in ("mp4", "webm"):
                        fmt.update({"video": f})

                self._fps_check(format_fps, chosen_fps),  # Check for chosen fps

        audio = fmt.get("audio")
        chosen_video = fmt.get("video")
        self.file_ext = chosen_video["video_ext"]

        if not audio:
            return [chosen_video]

        else:
            res = {
                "format_id": f'{chosen_video["format_id"]}+{audio["format_id"]}',
                "ext": chosen_video["ext"],
                "requested_formats": [chosen_video, audio],
                "protocol": f'{chosen_video["protocol"]}+{audio["protocol"]}',
            }

            return [res]

    def _get_media_type(self, format_resolution: str, chosen_resolution: int):
        if format_resolution[0] == "audio only":
            return "audio"

        if (chosen_resolution in format_resolution) or (
            f"{chosen_resolution}p" in format_resolution
        ):
            return "video"

        return False

    def _fps_check(self, format_fps: int, chosen_fps: int):
        if format_fps == chosen_fps or not chosen_fps:
            return True

        return False

    def _check_audio(self, *args):
        has_audio = []
        for param in args:
            if not param or param == "none":
                has_audio.append(False)
            else:
                has_audio.append(True)

        if any(has_audio):
            return True

        return False

    # Parse resolution and fps from incoming quality string
    def _parse_quality(self, chosen_quality: str) -> tuple[int, int]:
        quality = chosen_quality.strip()

        res_idx = quality.find("p")
        fps_idx = quality.find("f")

        quality = (
            int(quality[:res_idx]),
            int(quality[res_idx + 1 : fps_idx]) if fps_idx != -1 else None,
        )

        return quality

    def download(self):
        self.ydl.download(self.url)

        result = {
            "uuid": self.file_key,
            "ext": self.file_ext,
            "duration": self.duration_seconds,
            "thumb": self.thumbnail,
            "title": self.title,
            }
        
        return result



def get_media_data(media: Downloader):
    data = MediaData(
        user_id=media.user_id,
        name=media.title,
        resource=media.resource,
        duration=media.duration,
        image_url=media.thumbnail,
        media_url=media.url,
        qualities=media.qualities,
    )

    return data
