"""Single-origin ASGI entry point for the hosted development preview."""

from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from apps.api.main import app as api_app, reviewer_auth_response


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with api_app.router.lifespan_context(api_app):
        yield


app = FastAPI(title="GigBid development preview", lifespan=lifespan)


@app.middleware("http")
async def protect_public_preview(request: Request, call_next):
    denial = reviewer_auth_response(request)
    return denial if denial is not None else await call_next(request)


app.mount("/api", api_app)
web_dist = Path(os.getenv("GIGBID_WEB_DIST", Path(__file__).resolve().parents[2] / "apps" / "web" / "dist"))
if web_dist.is_dir():
    app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
