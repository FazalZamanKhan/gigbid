# Portfolio MCP server

Development server built with the official Python MCP SDK. It currently exposes **synthetic demonstration evidence only**; publication as a reusable package is pending the real portfolio corpus and tests.

```bash
pip install -e .
python -m mcp_servers.portfolio.server
```

Tools: `search_evidence`, `get_case_study`, `list_skills`. Resource template: `portfolio://case/{id}`. Prompt: `answer_screening_question`.
