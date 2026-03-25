# ADR-004: No Go Backend Modifications

## Status
Accepted

## Context
The Homebox fork needs to stay mergeable with upstream. Go backend changes (ent schema, routes, handlers) create the hardest merge conflicts.

## Decision
All new functionality is implemented in:
1. Vue frontend (new pages, components, composables)
2. HBC sidecar (Python, separate service)
3. Affine bridge (frontend composable calling Affine API directly)

The Go backend remains unmodified from upstream.

## Rationale
- Go backend changes require ent schema migrations, handler code, route registration
- These files change frequently upstream (feature additions, bug fixes)
- Frontend-only changes conflict in only 4 predictable files (nav, item page, locales, config)
- HBC already provides batch item creation via its API (wraps Homebox's Go API)
- Affine's GraphQL API is callable directly from the browser
