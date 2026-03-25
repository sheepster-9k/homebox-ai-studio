# Affine API — Technical Reference

**Instance**: Casper (192.168.42.99), port 3010, v0.26.3
**Database**: PostgreSQL with pgvector (55 tables)
**Search**: ManticoreSearch indexer

## Primary API: GraphQL (`/graphql`)

### Key Queries
- `currentUser` — authenticated user info
- `workspace(id)` — workspace details
- `workspaces` — list user's workspaces

### Key Mutations (relevant to integration)
- `applyDocUpdates(workspaceId, docId, updates)` — apply CRDT updates to doc
- `publishDoc(workspaceId, docId)` — make doc publicly accessible
- `generateUserAccessToken(name)` — create API token
- `revokeUserAccessToken(id)` — revoke token
- `createCopilotSession(workspaceId, docId)` — AI chat session
- `addWorkspaceEmbeddingFiles(workspaceId, files)` — add files to RAG index

## REST Endpoints (relevant)
- `GET /rpc/workspaces/:id/docs/:id/markdown` — export doc as markdown
- `GET /rpc/workspaces/:id/docs/:id/content` — get doc content
- `POST /rpc/workspaces/:id/docs/:id/diff` — apply document diffs
- `PUT /api/storage/upload` — file upload
- `GET /api/workspaces/:id/blobs/:name` — get blob/file

## MCP Integration
- `GET /api/workspaces/:id/mcp` — list MCP servers
- `POST /api/workspaces/:id/mcp` — register MCP server

## Authentication
- Access tokens via `generateUserAccessToken` mutation
- Bearer token in Authorization header
- Session cookies for browser access

## Data Model (key tables)
- `workspace_pages` — documents (title, summary, mode, defaultRole)
- `snapshots` — binary blob content (CRDT state)
- `updates` — incremental doc updates
- `blobs` — media files
- `ai_workspace_embeddings` — pgvector embeddings for RAG
- `ai_sessions_metadata` / `ai_sessions_messages` — AI chat

## Integration Strategy
- Use GraphQL for doc creation and management
- Use RPC for markdown export/import
- Store Homebox item ID in doc metadata (`<!-- homebox:item:UUID -->`)
- Store Affine doc ID in Homebox custom field (`affine_doc_id`)
- Proxy through NPM if CORS needed (`/affine/graphql` → `localhost:3010/graphql`)
