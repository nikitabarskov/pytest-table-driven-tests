from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from nikitabarskov.url_shortener.db import get_engine, init
from nikitabarskov.url_shortener.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    db = get_engine()
    init(db)
    yield


app = FastAPI(
    title="URL Shortener",
    lifespan=lifespan,
)

app.include_router(router)
