from fastapi import APIRouter, HTTPException, Query

from .service import (
    VideoDownload, 
    get_video_data as get_data
    )


router = APIRouter(
    prefix="/v",
    tags=["video"],
    responses={404: {"decription": "Not found"}}
)

# добавить &download=true/false
@router.get("")
def get_video_data(
    url: str = Query(min_length=20),
    user_id: int = Query(gt=0)
    ):
    try:
        video = VideoDownload(
            url=url,
            user_id=user_id,
            meta=True
            )
            
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Video wasn't found: {e}")

    video_data = get_data(video)

    return video_data.dict()
    


