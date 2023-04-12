from fastapi import FastAPI
from downloader_app.router import router


def get_application():
    _app = FastAPI()
    _app.include_router(router)

    return _app


app = get_application()


