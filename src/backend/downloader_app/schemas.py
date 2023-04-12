from pydantic import BaseModel
from typing import List


class VideoData(BaseModel):
    user_id: int
    name: str
    resource: str
    duration: str
    image_url: str
    video_url: str
    qualities: List[str]

    def __repr__(self) -> str:
        return f"<Class VideoData>(name={self.name}, duration={self.duration}, \
            image_url={self.image_url}, resourse={self.resource} \
            video_url={self.video_url}, qualities={self.qualities})"
