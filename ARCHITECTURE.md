# Architecture

## System Overview

```
+------------------+     +------------------+     +------------------+
|   Homebox        |     |   HBC Sidecar    |     |   Affine         |
|   (Go + Nuxt)    |---->|   (Python/Fast)  |     |   (Node/GraphQL) |
|   Port 7745      |     |   Port 8000      |     |   Port 3010      |
|   SQLite         |     |   Stateless      |     |   PostgreSQL     |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        +-- Docker Network ------+------------------------+
        |
   Nginx Reverse Proxy (NPM)
        |
   hb.neon-sheep.net (HTTPS)
     /        -> Homebox (:7745)
     /hbc/*   -> HBC (:8000)
```

## Data Flow: Studio Bulk Capture

```
1. User uploads photo of shelf
   |
2. Browser sends image to HBC /api/tools/vision/detect
   | (via /hbc/ proxy, same-origin HTTPS)
   |
3. HBC compresses image, sends to LLM with vision prompt
   | (Qwen-122B on local GPU cluster)
   |
4. LLM returns detected items (name, qty, description, tags, etc.)
   |
5. Browser displays items in grid/canvas with crop regions
   |
6. User reviews, edits, selects location, removes false positives
   |
7. Browser sends batch to HBC /api/items (BatchCreateRequest)
   | (HBC creates items in Homebox via internal API)
   |
8. Items appear in Homebox inventory with AI-detected metadata
   |
9. (Optional) Affine pages auto-created for each imported item
```

## Frontend Architecture

```
pages/companion/studio.vue          -- Orchestrator (step navigation)
  |
  +-- components/Studio/
  |     +-- CapturePanel.vue        -- Camera/upload
  |     +-- DetectionCanvas.vue     -- Interactive bounding boxes (Phase 2)
  |     +-- CropOverlay.vue         -- Draggable crop regions (Phase 2)
  |     +-- ItemGrid.vue            -- Card grid of detected items
  |     +-- ItemReviewCard.vue      -- Single item review/edit
  |     +-- ItemReviewTable.vue     -- Table view (Phase 4)
  |     +-- BatchActionBar.vue      -- Import controls
  |     +-- SessionManager.vue      -- Save/load sessions (Phase 3)
  |
  +-- stores/studio.ts              -- Pinia session state
  +-- composables/use-companion.ts  -- HBC API client
  +-- lib/studio/
        +-- image-processing.ts     -- Canvas crop extraction
        +-- canvas-math.ts          -- Geometry utilities (Phase 2)
        +-- session-storage.ts      -- IndexedDB wrapper (Phase 3)
```

## Key Decisions

See `docs/decisions/` for full ADRs.

- **001**: Single-page Studio with component steps (not sub-routes) — session state stays in memory
- **002**: IndexedDB for session persistence — images are multi-MB, exceeds localStorage limits
- **003**: Affine linking via Homebox custom fields — no Go backend changes needed
- **004**: No Go backend modifications — keeps fork shallow, upstream merges clean
