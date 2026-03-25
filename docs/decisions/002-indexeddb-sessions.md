# ADR-002: IndexedDB for Session Persistence

## Status
Accepted

## Context
Studio sessions contain base64 image data (multiple MB per photo). Need to persist across page refreshes.

## Decision
Use IndexedDB (via raw API or idb-keyval) instead of localStorage.

## Rationale
- localStorage limit: 5-10MB (varies by browser)
- A single high-res photo can be 2-5MB base64
- A studio session with 3 photos + crops can easily exceed 20MB
- IndexedDB has no practical size limit
- Supports structured data (sessions, items, crops) natively
