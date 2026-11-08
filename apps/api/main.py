"""Development API backed by synthetic MCP services and optional durable checkpoints."""

from contextlib import asynccontextmanager
import base64
import binascii
import os
import secrets
from uuid import uuid4
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from langgraph.types import Command

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from mcp_servers.marketplace.adapters.demo import DemoMarketplace
from mcp_servers.marketplace.client import DemoMCPMarketplace
from mcp_servers.workspace.client import DemoWorkspace

marketplace = DemoMCPMarketplace() if os.getenv("GIGBID_MARKETPLACE") == "demo_mcp" else DemoMarketplace()
workspace = DemoWorkspace()
graph = build_bid_graph(marketplace)
conversation_graph = build_conversation_graph(marketplace, workspace)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global graph, conversation_graph
    if os.getenv("GIGBID_CHECKPOINT_BACKEND", "memory") == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        database_url = os.environ["DATABASE_URL"]
        async with AsyncPostgresSaver.from_conn_string(database_url) as checkpointer:
            await checkpointer.setup()
            graph = build_bid_graph(marketplace, checkpointer=checkpointer)
            conversation_graph = build_conversation_graph(marketplace, workspace, checkpointer=checkpointer)
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


class ConversationInput(BaseModel):
    incoming: str
    day: date | None = None


def _view(run_id: str, snapshot):
    pending = bool(snapshot.next and "approval" in snapshot.next)
    return {"run_id": run_id, "status": "awaiting_approval" if pending else "finished", "state": snapshot.values}


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "development-demo", "marketplace": os.getenv("GIGBID_MARKETPLACE", "demo")}


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


@app.post("/jobs/{job_id}/conversations")
async def start_conversation(job_id: str, body: ConversationInput):
    if not body.incoming.strip():
        raise HTTPException(422, "Incoming message is empty")
    try:
        await marketplace.get_job(job_id)
    except KeyError:
        raise HTTPException(404, "Job not found")
    run_id = str(uuid4())
    config = {"configurable": {"thread_id": run_id}}
    day = body.day or date.today() + timedelta(days=1)
    await conversation_graph.ainvoke({"run_id": run_id, "job_id": job_id, "incoming": body.incoming, "day": day.isoformat(), "events": []}, config)
    return _view(run_id, await conversation_graph.aget_state(config))


@app.get("/conversations/{run_id}")
async def get_conversation(run_id: str):
    config = {"configurable": {"thread_id": run_id}}
    snapshot = await conversation_graph.aget_state(config)
    if not snapshot.values:
        raise HTTPException(404, "Conversation not found")
    return _view(run_id, snapshot)


@app.post("/conversations/{run_id}/approval")
async def approve_conversation(run_id: str, body: ApprovalInput):
    config = {"configurable": {"thread_id": run_id}}
    snapshot = await conversation_graph.aget_state(config)
    if not snapshot.values:
        raise HTTPException(404, "Conversation not found")
    if "approval" not in snapshot.next:
        raise HTTPException(409, "Conversation is not awaiting approval")
    await conversation_graph.ainvoke(Command(resume=body.model_dump(exclude_none=True)), config)
    return _view(run_id, await conversation_graph.aget_state(config))
