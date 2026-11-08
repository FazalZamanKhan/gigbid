"""Local mock calendar and email-draft tools. No external delivery occurs."""

from datetime import date, datetime, time, timezone
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


mcp = FastMCP("GigBid Development Workspace")


@contextmanager
def _connection():
    path = Path(os.getenv("GIGBID_WORKSPACE_DB", "/tmp/gigbid_workspace.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.execute("CREATE TABLE IF NOT EXISTS holds (idempotency_key TEXT PRIMARY KEY, slot TEXT UNIQUE NOT NULL)")
    connection.execute("CREATE TABLE IF NOT EXISTS email_drafts (idempotency_key TEXT PRIMARY KEY, recipient TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL)")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _candidate_slots(day: date) -> list[str]:
    return [datetime.combine(day, time(hour, 0), tzinfo=timezone.utc).isoformat() for hour in (9, 11, 15)]


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_free_slots(day: str) -> list[str]:
    """List available synthetic UTC interview slots for an ISO date. Read only."""
    try:
        target = date.fromisoformat(day)
    except ValueError:
        return []
    with _connection() as connection:
        occupied = {row[0] for row in connection.execute("SELECT slot FROM holds")}
    return [slot for slot in _candidate_slots(target) if slot not in occupied]


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
def create_tentative_hold(slot: str, idempotency_key: str, dry_run: bool = False) -> dict:
    """Preview or reserve one local mock interview slot. Never books a real calendar."""
    try:
        parsed = datetime.fromisoformat(slot)
    except ValueError:
        return {"error": "invalid_slot"}
    if parsed.tzinfo is None or slot not in _candidate_slots(parsed.date()) or not idempotency_key:
        return {"error": "invalid_slot"}
    preview = {"slot": slot, "idempotency_key": idempotency_key, "tentative": True}
    if dry_run:
        return {**preview, "dry_run": True}
    with _connection() as connection:
        existing = connection.execute("SELECT slot FROM holds WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        if existing:
            if existing[0] != slot:
                return {"error": "idempotency_conflict", "slot": existing[0]}
            return {**preview, "slot": existing[0], "hold_id": f"hold-{idempotency_key}"}
        try:
            connection.execute("INSERT INTO holds (idempotency_key, slot) VALUES (?, ?)", (idempotency_key, slot))
        except sqlite3.IntegrityError:
            return {"error": "slot_unavailable", "slot": slot}
    return {**preview, "hold_id": f"hold-{idempotency_key}"}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
def create_email_draft(recipient: str, subject: str, body: str, idempotency_key: str, dry_run: bool = False) -> dict:
    """Preview or save a local mock email draft. Never sends email."""
    if not recipient or "@" not in recipient or not subject.strip() or not body.strip() or not idempotency_key:
        return {"error": "invalid_draft"}
    preview = {"recipient": recipient, "subject": subject, "body": body, "idempotency_key": idempotency_key}
    if dry_run:
        return {**preview, "dry_run": True}
    with _connection() as connection:
        existing = connection.execute("SELECT recipient, subject, body FROM email_drafts WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        if existing:
            if existing != (recipient, subject, body):
                return {"error": "idempotency_conflict", "draft_id": f"email-draft-{idempotency_key}"}
            return {**preview, "recipient": existing[0], "subject": existing[1], "body": existing[2], "draft_id": f"email-draft-{idempotency_key}"}
        connection.execute("INSERT INTO email_drafts (idempotency_key, recipient, subject, body) VALUES (?, ?, ?, ?)", (idempotency_key, recipient, subject, body))
    return {**preview, "draft_id": f"email-draft-{idempotency_key}"}


if __name__ == "__main__":
    mcp.run()
