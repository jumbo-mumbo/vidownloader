from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from .service import Downloader, get_media_data as get_data

import os

# add /api/v...
router = APIRouter(
    prefix="", tags=["media"], responses={404: {"decription": "Not found"}}
)


# добавить &download=true/false
@router.get("/d")
def media_manager(
    url: str = Query(min_length=32),
    user_id: int = Query(gt=0),
    quality: str | None = None,
):
    try:
        media = Downloader(
            url=url, user_id=user_id, quality=quality
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Media wasn't found: {e}")

    if not quality:
        media_data = get_data(media)
        return media_data.dict()

    file_data = media.download()
    response = {"data": file_data}

    return response


@router.get("/d")
def delete_media(file_path: str = Query(min_length=32)):
    pass