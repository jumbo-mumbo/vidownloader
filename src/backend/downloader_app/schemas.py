from pydantic import BaseModel
from typing import List


class MediaData(BaseModel):
    user_id: int
    name: str
    resource: str
    duration: str
    image_url: str
    media_url: str
    qualities: List[str]

    def __repr__(self) -> str:
        return f"<Class MediaData>(name={self.name}, duration={self.duration}, \
            image_url={self.image_url}, resourse={self.resource} \
            media_url={self.media_url}, qualities={self.qualities})"
