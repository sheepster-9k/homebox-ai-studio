# ADR-001: Single-Page Studio with Component Steps

## Status
Accepted

## Context
The Studio workflow (capture → detect → review → import) is sequential and stateful. Two options: sub-routes (/studio/capture, /studio/detect, etc.) or a single page with component visibility toggled by state.

## Decision
Single page (`studio.vue`) with step components controlled by the Pinia store's `currentStep` field.

## Rationale
- Sub-routes would require URL-driven state management or redundant store hydration on each navigation
- Session state (images, detected items, crop regions) is large and memory-resident
- A single page keeps the workflow self-contained
- No risk of losing state on browser back/forward navigation
- Session persistence (IndexedDB) handles page refresh/close recovery
