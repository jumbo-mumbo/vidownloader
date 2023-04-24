import os
import yt_dlp

from uuid import uuid4
from .schemas import VideoData
from .utils import time_format, format_bytes, get_resolution_height, check_thumbnail


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
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            meta = ydl.extract_info(self.url, download=False)
            self.resource = list(ydl._ies_instances.keys())[
                0
            ]  # Extract video source (Youtube, Vk, etc.)
            self.title = meta.get("title", meta)
            self.duration = time_format(meta.get("duration", meta))
            self.thumbnail = self._get_thumbnail(meta.get("thumbnails", meta))
            self.ydl = ydl

    def _get_thumbnail(self, thumbnails):
        for t in thumbnails[::-1]:
            url = t["url"]
            if not url.endswith(".webp") and check_thumbnail(url):
                return url

    def _get_qualities(self):
        ydl = self.ydl
        meta = ydl.extract_info(self.url, download=False)
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


class VideoDownload:
    def __init__(
        self,
        url: str,
        user_id: int,
        metadata: bool = False,
        quality: str | None = None,
    ):
        self.url = url
        self.user_id = user_id

        if not metadata:
            self.quality = quality
            self.file_key = uuid4()
            self.file_ext = "mp4"
            self.path = os.getcwd().removesuffix("/src/backend")
            self.ydl = self._get_ydl()
        else:
            self.meta = VideoMetadata(url=self.url)

    def _get_ydl(self):
        options = self._get_options()
        with yt_dlp.YoutubeDL(options) as ydl:
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
        self.video_ext = chosen_video["video_ext"]

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
        if chosen_quality:
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
        return self.file_key, self.file_ext

    def delete(self):
        pass


def get_video_data(video: VideoDownload):
    v = video
    data = VideoData(
        user_id=v.user_id,
        name=v.meta.title,
        resource=v.meta.resource,
        duration=v.meta.duration,
        image_url=v.meta.thumbnail,
        video_url=v.meta.url,
        qualities=v.meta.qualities,
    )

    return data
