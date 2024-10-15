from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from src.models import MODEL
from src.core import engine
from src.routes import router_files, router_transactions


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[Any]:
    assert app
    MODEL.metadata.create_all(engine)
    yield


app = FastAPI(title="BookKeeping", lifespan=lifespan)
app.include_router(router_files)
app.include_router(router_transactions)


@app.get("/health_check")
def home():
    return True
