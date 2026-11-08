# Portfolio MCP server

Read-only server built with the official Python MCP SDK. It currently exposes **synthetic demonstration evidence only**. Do not present its case studies as a real freelancer's history.

From a public Git revision, an MCP client can launch it over stdio with [uvx](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx --from git+https://github.com/FazalZamanKhan/gigbid.git@portfolio-v0.1.0 gigbid-portfolio-mcp
```

The command stays running while the MCP client is connected; it is not a web page. The server is a reusable development package, while the evidence corpus remains synthetic until the user supplies consented portfolio data.

For a local checkout:

```bash
python -m pip install -e .
gigbid-portfolio-mcp
```

Tools: `search_evidence`, `get_case_study`, `list_skills`. Resource template: `portfolio://case/{id}`. Prompt: `answer_screening_question`. `search_evidence` defaults to keyword matching; optional `variant=v0|v1|v2|v3|v4|v8` uses the `rag` extra and downloads local embedding or reranker models on first use. These variants have only been smoke-tested on synthetic data.
