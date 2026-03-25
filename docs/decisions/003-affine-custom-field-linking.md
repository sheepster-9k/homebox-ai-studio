# ADR-003: Affine Linking via Homebox Custom Fields

## Status
Accepted

## Context
Need bidirectional links between Homebox items and Affine documents without modifying Homebox's Go backend.

## Decision
Store the Affine document ID in a Homebox custom field named `affine_doc_id`. Store the Homebox item ID in the Affine document as an HTML comment `<!-- homebox:item:UUID -->`.

## Rationale
- Custom fields are first-class in Homebox (full CRUD via existing API)
- No Go code changes = no new merge conflict points with upstream
- Visible and editable in the Homebox UI
- HTML comments in Affine docs are invisible to users but parseable
- No database schema changes needed on either side
