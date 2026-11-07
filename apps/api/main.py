"""Development API. Demo state is process-local and not production durable."""

from contextlib import asynccontextmanager
import base64
import binascii
import os
import secrets
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from langgraph.types import Command

from agent.graphs.bid_graph import build_bid_graph
from mcp_servers.marketplace.adapters.demo import DemoMarketplace

marketplace = DemoMarketplace()
graph = build_bid_graph(marketplace)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global graph
    if os.getenv("GIGBID_CHECKPOINT_BACKEND", "memory") == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        database_url = os.environ["DATABASE_URL"]
        async with AsyncPostgresSaver.from_conn_string(database_url) as checkpointer:
            await checkpointer.setup()
            graph = build_bid_graph(marketplace, checkpointer=checkpointer)
            yield
    else:
        yield


app = FastAPI(title="GigBid development API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def reviewer_auth(request: Request, call_next):
    username = os.getenv("GIGBID_REVIEWER_USERNAME")
    password = os.getenv("GIGBID_REVIEWER_PASSWORD")
    if request.url.path == "/health" or request.method == "OPTIONS":
        return await call_next(request)
    if not username and not password:
        return await call_next(request)
    if not username or not password:
        return Response("Reviewer authentication is misconfigured", status_code=503)
    authorization = request.headers.get("authorization", "")
    try:
        scheme, encoded = authorization.split(" ", 1)
        supplied = base64.b64decode(encoded, validate=True).decode("utf-8")
        supplied_user, supplied_password = supplied.split(":", 1)
    except (ValueError, UnicodeDecodeError, binascii.Error):
        scheme = supplied_user = supplied_password = ""
    if scheme.casefold() != "basic" or not (
        secrets.compare_digest(supplied_user, username)
        and secrets.compare_digest(supplied_password, password)
    ):
        return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="GigBid Reviewer"'})
    return await call_next(request)


class ApprovalInput(BaseModel):
    approved: bool
    text: str | None = None
    reason: str | None = None


def _view(run_id: str, snapshot):
    pending = bool(snapshot.next and "approval" in snapshot.next)
    return {"run_id": run_id, "status": "awaiting_approval" if pending else "finished", "state": snapshot.values}


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "development-demo"}


@app.get("/jobs")
async def list_jobs():
    return [job.model_dump() for job in await marketplace.list_jobs()]


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        return (await marketplace.get_job(job_id)).model_dump()
    except KeyError:
        raise HTTPException(404, "Job not found")


@app.post("/jobs/{job_id}/runs")
async def run_job(job_id: str):
    try:
        await marketplace.get_job(job_id)
    except KeyError:
        raise HTTPException(404, "Job not found")
    run_id = str(uuid4())
    config = {"configurable": {"thread_id": run_id}}
    await graph.ainvoke({"job_id": job_id, "events": []}, config)
    return _view(run_id, await graph.aget_state(config))


@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    config = {"configurable": {"thread_id": run_id}}
    snapshot = await graph.aget_state(config)
    if not snapshot.values:
        raise HTTPException(404, "Run not found")
    return _view(run_id, snapshot)


@app.post("/runs/{run_id}/approval")
async def approve_run(run_id: str, body: ApprovalInput):
    config = {"configurable": {"thread_id": run_id}}
    snapshot = await graph.aget_state(config)
    if not snapshot.values:
        raise HTTPException(404, "Run not found")
    if "approval" not in snapshot.next:
        raise HTTPException(409, "Run is not awaiting approval")
    await graph.ainvoke(Command(resume=body.model_dump(exclude_none=True)), config)
    return _view(run_id, await graph.aget_state(config))
