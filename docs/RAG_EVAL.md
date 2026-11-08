# Retrieval experiment harness

The harness implements V0 fixed-chunk dense cosine retrieval, V1 requirement decomposition, V2 dense/BM25 reciprocal rank fusion, V3 cross-encoder reranking, V4 training-outcome-aware reranking, and a V8 corrective re-query/abstention LangGraph subgraph. It reports evidence Recall@5, MRR, nDCG@10, abstention rate, and p95 retrieval latency. V8 grades retrieved text against query terms and re-queries by requirement when weak; a broader calibrated evidence grader is still needed.

Use a real embedding and cross-encoder model with the optional dependency:

```bash
python -m pip install -e '.[rag]'
python -m evals.runners.retrieval_eval \
  --corpus path/to/dev_corpus.jsonl \
  --cases path/to/dev_cases.jsonl \
  --dataset-label official-dev \
  --output evals/results/official_retrieval.json
```

The command does not download or create the official data. `--corpus` requires JSONL records with `id`, `text`, optional `source_id`, and optional `outcome_score` in `[0, 1]`. Documents without `source_id` are split into fixed 120-word chunks with 20-word overlap. Records with `source_id` are treated as pre-chunked. `--cases` requires `id`, `query`, `gold_evidence_ids`, and optional `requirements`, `persona`, and `job_type`. Gold IDs refer to source IDs. Outcome scores must be computed from training history only; never copy reply/hire outcomes from the dev or test cases into the corpus. The evaluator caches document embeddings before timing queries and reports index build time separately.

The current Python tests inject tiny count vectors and a token reranker to verify ranking control flow. They are **not** semantic quality measurements. No official GigSim, corpus, labels, or outcome history was supplied with the Classroom assignment at the time of this work. A result from this harness therefore cannot be called an assignment result until those inputs and model versions are recorded. The harness does not measure proposal quality, decision F1, scam detection, price fairness, cost, or GigSim reply/hire outcomes.

For local development, the Portfolio MCP `search_evidence` tool accepts `variant` and `requirements`. Set `GIGBID_RAG_VARIANT=v2` when running the API in a Python environment with the `rag` extra to make the bid graph use measured-style hybrid retrieval on the synthetic demo corpus. The default remains the small keyword demo until an official dev-set experiment identifies the model and variant to deploy. The base Docker image omits the optional model package.
