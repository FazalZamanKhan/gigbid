# ADR 0001: One marketplace port

Status: accepted for development.

The graph depends on a typed `MarketplacePort` interface. The local synthetic adapter is used only while waiting for GigSim. The provided GigSim API and the official Upwork MCP adapter will implement the same contract. This keeps marketplace-specific paths and authentication out of graph nodes and makes a policy change local to configuration or the relevant adapter.

The current port covers only job listing, job detail, and draft creation. It will grow to cover client history, Connects, proposals, and messages after the starter kit's API is available.
