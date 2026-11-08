# MCP tool inventory (development)

| Tool | Server | Mode | Auth | Status |
| --- | --- | --- | --- | --- |
| `search_evidence(requirement, k)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `get_case_study(id)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `list_skills()` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `list_jobs()` | Development Marketplace | Read | Local stdio | Implemented on synthetic jobs |
| `get_job(job_id)` | Development Marketplace | Read | Local stdio | Implemented on synthetic jobs |
| `create_proposal_draft(job_id, text, idempotency_key, dry_run)` | Development Marketplace | Draft write | Local stdio and graph approval | Synthetic draft only; never submits a bid |
| `send_message(job_id, text, idempotency_key, dry_run)` | Development Marketplace | Message write | Local stdio and graph approval | Synthetic message only; never contacts a client |
| `get_free_slots(day)` | Development Workspace | Read | Local stdio | Synthetic UTC slots |
| `create_tentative_hold(slot, idempotency_key, dry_run)` | Development Workspace | Local write | Local stdio | Idempotent SQLite mock hold |
| `create_email_draft(recipient, subject, body, idempotency_key, dry_run)` | Development Workspace | Local write | Local stdio | Idempotent SQLite mock draft; never sends email |

The development MCP servers have read-only or idempotent tool annotations. They are not the instructor's GigSim or a real productivity account. Production HTTP bearer auth, schema snapshots, and third-party server trust rationales are pending. Synthetic marketplace writes are behind human approval interrupts and the typed marketplace port.
