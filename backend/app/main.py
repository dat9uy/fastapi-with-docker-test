import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core import config, events


def get_application():
    fastapi_app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.add_event_handler("startup", events.create_start_app_handler(fastapi_app))
    fastapi_app.add_event_handler("shutdown", events.create_stop_app_handler(fastapi_app))

    fastapi_app.include_router(api_router, prefix="/api")

    return fastapi_app


app = get_application()

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=1)
