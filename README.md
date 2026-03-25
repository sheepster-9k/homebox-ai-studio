# Homebox AI Studio

An AI-powered inventory management platform built on top of [Homebox](https://github.com/sysadminsmedia/homebox) and [Homebox Companion](https://github.com/Duelion/homebox-companion).

## Vision

Turn any camera into an inventory scanner. Photograph a shelf, closet, or room and let AI detect, catalog, and organize everything — then link it to your knowledge base for full lifecycle management.

## Architecture

```
Browser
  |
  +-- Homebox (forked, sheepster-9k/homebox)
  |     |-- /companion/studio    AI Capture Studio
  |     |-- /companion/chat      AI Inventory Chat
  |     |-- /companion/capture   Quick Snap & Catalog
  |     |-- /companion/qr        QR/Barcode Scanner
  |     +-- /hbc/*               Reverse proxy to HBC
  |
  +-- HBC Sidecar (Homebox Companion)
  |     |-- POST /api/tools/vision/detect    Multi-item detection
  |     |-- POST /api/tools/vision/analyze   Deep item analysis
  |     |-- POST /api/tools/vision/correct   AI correction with feedback
  |     |-- POST /api/items                  Batch item creation
  |     +-- POST /api/chat/stream            Streaming AI chat
  |
  +-- Affine (Knowledge Base)
        |-- GraphQL /graphql     Document CRUD, embeddings, AI
        +-- RPC /rpc/*           Markdown export, doc diffs
```

## Components

| Component | Description | Code Location |
|-----------|-------------|---------------|
| **AI Studio** | Bulk capture, interactive crop, review, batch import | `homebox/frontend/pages/companion/studio.vue` |
| **Companion Pages** | Chat, capture, QR scanner | `homebox/frontend/pages/companion/` |
| **Studio Store** | Session state, detected items, import progress | `homebox/frontend/stores/studio.ts` |
| **HBC Client** | Vision API, batch create, auth passthrough | `homebox/frontend/composables/use-companion.ts` |
| **Affine Bridge** | Doc creation, linking, reports | `homebox/frontend/composables/use-affine-bridge.ts` |
| **Project Docs** | Architecture, API logs, decisions | This repo (`homebox-ai-studio/`) |

## Repos

- **This repo**: Project documentation, architecture decisions, deployment configs
- **[sheepster-9k/homebox](https://github.com/sheepster-9k/homebox)**: Forked Homebox with all Studio code (AGPL-3.0)
- **Upstream**: [sysadminsmedia/homebox](https://github.com/sysadminsmedia/homebox) — synced daily via GitHub Actions

## Quick Start

```bash
# Deploy the full stack
cd docker/
docker compose -f docker-compose.studio.yml up -d

# Or build from source
cd /path/to/homebox-fork
docker build --build-arg NUXT_PUBLIC_HBC_URL=/hbc -t sheepster-9k/homebox:latest .
```

## Phases

- [x] Phase 0: Basic companion integration (chat, capture, QR)
- [ ] Phase 1: Studio core (capture -> detect -> review -> import)
- [ ] Phase 2: Interactive detection canvas with crop tools
- [ ] Phase 3: Session persistence (IndexedDB)
- [ ] Phase 4: Batch review table (TanStack Table)
- [ ] Phase 5: Affine bridge (knowledge base integration)
- [ ] Phase 6: Full stack Docker compose + CI/CD

## License

Code in the Homebox fork is AGPL-3.0 (same as upstream).
Documentation in this repo is MIT.
