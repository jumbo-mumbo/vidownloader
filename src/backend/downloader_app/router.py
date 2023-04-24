from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from .service import VideoDownload, get_video_data as get_data

import os

# add /api/v...
router = APIRouter(
    prefix="/v", tags=["video"], responses={404: {"decription": "Not found"}}
)


# добавить &download=true/false
@router.get("")
def get_video_data(
    url: str = Query(min_length=20),
    user_id: int = Query(gt=0),
    metadata: bool | None = None,
    quality: str | None = None,
):
    try:
        video = VideoDownload(
            url=url, user_id=user_id, metadata=metadata, quality=quality
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"Video wasn't found: {e}")

    if metadata:
        video_data = get_data(video)
        return video_data.dict()

    file_key, file_ext = video.download()
    response = {"uuid": file_key, "ext": file_ext}

    return response

    """
    # Downloading from server to user
    return FileResponse(
        path=pth + f"/media/{video_uuid}.{video_ext}",
        filename=f"{video_uuid}.{video_ext}")
    """
