# HBC Vision API — Technical Reference

## POST /api/tools/vision/detect

Multi-item detection from a single image.

**Parameters** (multipart form):
- `image` (file, required): Primary image
- `single_item` (bool, default false): Treat frame as one item
- `extra_instructions` (string, optional): User hint about contents
- `extract_extended_fields` (bool, default true): Extract manufacturer/model/serial
- `additional_images` (files, optional): More angles of same item(s)

**Response** `DetectionResponse`:
```json
{
  "items": [{
    "name": "string",
    "quantity": 1,
    "description": "string",
    "tag_ids": ["uuid"],
    "manufacturer": "string",
    "model_number": "string",
    "serial_number": "string",
    "purchase_price": 0.0,
    "purchase_from": "string",
    "notes": "string",
    "custom_fields": {"field_name": "value"},
    "duplicate_match": {
      "item_id": "uuid",
      "item_name": "string",
      "serial_number": "string",
      "location_name": "string"
    }
  }],
  "message": "string",
  "compressed_images": [{"data": "base64", "mime_type": "image/jpeg"}]
}
```

**Key behaviors**:
- Detection and image compression run in parallel
- Duplicate detection checks serial numbers against existing inventory
- Default tag IDs are filtered from AI suggestions (frontend adds them)
- Image quality configurable: RAW/HIGH(2560px)/MEDIUM(1920px)/LOW(1280px)

## POST /api/tools/vision/analyze

Deep analysis of a known item with multiple images.

**Parameters** (multipart form):
- `images` (files, required, 1+): Images of the item
- `item_name` (string, required): What the item is
- `item_description` (string, optional): Context

**Response** `AdvancedItemDetails`: Same fields as detect item, minus quantity/duplicate.

## POST /api/tools/vision/correct

Re-analyze with user feedback.

**Parameters** (multipart form):
- `image` (file): Original image
- `current_item` (JSON string): Current DetectedItemResponse
- `correction_instructions` (string, max 2000 chars): What to fix

**Response** `CorrectionResponse`: Updated items array + message.

## POST /api/items (Batch Create)

```json
{
  "items": [{
    "name": "string",
    "quantity": 1,
    "description": "string",
    "location_id": "uuid",
    "tag_ids": ["uuid"],
    "parent_id": "uuid",
    "serial_number": "string",
    "model_number": "string",
    "manufacturer": "string",
    "purchase_price": 0.0,
    "purchase_from": "string",
    "notes": "string",
    "insured": false,
    "custom_fields": {"field_name": "value"}
  }],
  "location_id": "uuid (fallback)"
}
```

**Response**: 200 (all ok) or 207 (partial): `{created: [], errors: [], message: ""}`

Two-step creation: basic fields first, then extended fields update. Failed items cleaned up.
