"""Single internal marketplace interface. Graph code never calls GigSim directly."""

from typing import Protocol
from agent.handoffs import JobSpec


class MarketplacePort(Protocol):
    async def list_jobs(self) -> list[JobSpec]: ...

    async def get_job(self, job_id: str) -> JobSpec: ...

    async def create_proposal_draft(
        self, job_id: str, text: str, idempotency_key: str, dry_run: bool = False
    ) -> dict: ...

    async def send_message(
        self, job_id: str, text: str, idempotency_key: str, dry_run: bool = False
    ) -> dict: ...
