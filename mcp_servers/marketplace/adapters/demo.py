"""Synthetic local adapter for development only; never used as R&D evidence."""

from agent.handoffs import JobSpec


DEMO_JOBS = [
    JobSpec(
        id="demo-1",
        title="Build a Python analytics dashboard",
        description="Need a Python developer to clean CSV data and build an accessible dashboard.",
        skills=["Python", "Data analysis", "Dashboard"],
        budget_min=300,
        budget_max=600,
        connects_cost=8,
        client_rating=4.7,
    ),
    JobSpec(
        id="demo-2",
        title="Free sample project, contact me on WhatsApp",
        description="Send a free sample and contact me off platform before I hire anyone.",
        skills=["Python"],
        budget_min=0,
        budget_max=50,
        connects_cost=12,
        client_rating=2.1,
    ),
]


class DemoMarketplace:
    def __init__(self):
        self.drafts: dict[str, dict] = {}

    async def list_jobs(self) -> list[JobSpec]:
        return DEMO_JOBS

    async def get_job(self, job_id: str) -> JobSpec:
        for job in DEMO_JOBS:
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    async def create_proposal_draft(
        self, job_id: str, text: str, idempotency_key: str, dry_run: bool = False
    ) -> dict:
        preview = {"job_id": job_id, "text": text, "idempotency_key": idempotency_key, "cost_connects": (await self.get_job(job_id)).connects_cost}
        if dry_run:
            return {**preview, "dry_run": True}
        return self.drafts.setdefault(idempotency_key, {**preview, "draft_id": f"draft-{idempotency_key}"})
