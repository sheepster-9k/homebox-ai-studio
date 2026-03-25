# Homebox API — Complete Reference (v0.24.2)

Source: OpenAPI 3.0 spec from `backend/app/api/static/docs/openapi-3.json`
**58 endpoints, 101 schemas**, Bearer token auth.

## MCP Server Viability: EXCELLENT

This API is a near-perfect MCP target:
- Full CRUD on all entities (items, locations, tags, templates, maintenance)
- Rich query/filter on items endpoint
- File attachment upload/download
- Statistics and reporting
- Barcode lookup
- Export/import (CSV)
- All responses are JSON with consistent schema

---

## Items (Core — 15 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/items` | Query all items (paginated, filterable) |
| POST | `/v1/items` | Create item |
| GET | `/v1/items/{id}` | Get item (full detail with fields, attachments, location, tags) |
| PUT | `/v1/items/{id}` | Update item (full replace) |
| PATCH | `/v1/items/{id}` | Partial update (location, quantity, tags only) |
| DELETE | `/v1/items/{id}` | Delete item |
| POST | `/v1/items/{id}/duplicate` | Duplicate item (with options: copy attachments, fields, maintenance) |
| GET | `/v1/items/{id}/path` | Get full hierarchy path |
| GET | `/v1/items/export` | Export all items as CSV |
| POST | `/v1/items/import` | Import items from CSV |
| GET | `/v1/items/fields` | Get all custom field names in use |
| GET | `/v1/items/fields/values` | Get all custom field name+value pairs |
| GET | `/v1/assets/{id}` | Get item by asset ID (barcode lookup) |
| GET | `/v1/products/search-from-barcode` | Search product DB by barcode/EAN |
| POST | `/v1/qrcode` | Generate QR code image |

### ItemCreate schema
```json
{
  "name": "string (required, 1-255 chars)",
  "description": "string (max 1000)",
  "locationId": "uuid",
  "parentId": "uuid (optional, for sub-items)",
  "quantity": "integer (default 1)",
  "tagIds": ["uuid"]
}
```

### ItemOut schema (31 fields)
```
id, name, description, quantity, archived, insured
assetId, imageId, thumbnailId
locationId → location (LocationSummary)
tags[] (TagSummary)
fields[] (ItemField: name, type, textValue, numberValue, booleanValue)
attachments[] (ItemAttachment: id, path, mimeType, primary, thumbnail)
manufacturer, modelNumber, serialNumber
purchasePrice, purchaseFrom, purchaseTime
soldPrice, soldTo, soldNotes, soldTime
warrantyExpires, warrantyDetails, lifetimeWarranty
notes, syncChildItemsLocations
parent (ItemSummary), createdAt, updatedAt
```

### ItemUpdate schema (25 fields — full replace)
Same as ItemOut minus computed fields. Includes `fields[]` for custom fields.

### ItemPatch schema (partial update)
```json
{ "id": "uuid", "locationId": "uuid", "quantity": 1, "tagIds": ["uuid"] }
```

### GET /v1/items query params
- `q` — search query
- `page`, `pageSize` — pagination
- `locations[]` — filter by location IDs
- `tags[]` — filter by tag IDs
- `parentIds[]` — filter by parent item
- `orderBy` — sort field
- `fields[]` — filter by custom field values

---

## Item Attachments (4 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/items/{id}/attachments` | Upload attachment (multipart) |
| GET | `/v1/items/{id}/attachments/{aid}` | Download attachment |
| PUT | `/v1/items/{id}/attachments/{aid}` | Update metadata (title, type, primary) |
| DELETE | `/v1/items/{id}/attachments/{aid}` | Delete attachment |

Types: `photo`, `manual`, `receipt`, `warranty`, `attachment`

---

## Locations (6 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/locations` | Get all (flat list with item counts) |
| POST | `/v1/locations` | Create location |
| GET | `/v1/locations/tree` | Get hierarchical tree |
| GET | `/v1/locations/{id}` | Get location (with children, items, total price) |
| PUT | `/v1/locations/{id}` | Update location |
| DELETE | `/v1/locations/{id}` | Delete location |

### LocationCreate: `{ name, description, parentId }`
### LocationOut: `{ id, name, description, children[], parent, totalPrice, itemCount, createdAt, updatedAt }`

---

## Tags (5 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/tags` | Get all tags |
| POST | `/v1/tags` | Create tag |
| GET | `/v1/tags/{id}` | Get tag (with items) |
| PUT | `/v1/tags/{id}` | Update tag |
| DELETE | `/v1/tags/{id}` | Delete tag |

### TagCreate: `{ name, description, color, icon, parentId }`
### TagOut: `{ id, name, description, color, icon, parent, children[], createdAt, updatedAt }`

---

## Maintenance (5 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/maintenance` | Query all maintenance entries (filterable) |
| GET | `/v1/items/{id}/maintenance` | Get maintenance for specific item |
| POST | `/v1/items/{id}/maintenance` | Create maintenance entry |
| PUT | `/v1/maintenance/{id}` | Update entry |
| DELETE | `/v1/maintenance/{id}` | Delete entry |

### MaintenanceEntry: `{ name, description, cost, scheduledDate, completedDate }`

---

## Templates (6 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/templates` | List all templates |
| POST | `/v1/templates` | Create template |
| GET | `/v1/templates/{id}` | Get template |
| PUT | `/v1/templates/{id}` | Update template |
| DELETE | `/v1/templates/{id}` | Delete template |
| POST | `/v1/templates/{id}/create-item` | Create item from template |

---

## Statistics (4 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/groups/statistics` | Overall stats (totals, value) |
| GET | `/v1/groups/statistics/locations` | Per-location item count + value |
| GET | `/v1/groups/statistics/purchase-price` | Value over time chart data |
| GET | `/v1/groups/statistics/tags` | Per-tag item count + value |

### GroupStatistics: `{ totalItems, totalLocations, totalTags, totalUsers, totalItemPrice, totalWithWarranty }`

---

## Actions (6 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/actions/ensure-asset-ids` | Assign asset IDs to items missing them |
| POST | `/v1/actions/ensure-import-refs` | Generate import references |
| POST | `/v1/actions/create-missing-thumbnails` | Generate thumbnails for photos |
| POST | `/v1/actions/set-primary-photos` | Auto-set primary photo on items |
| POST | `/v1/actions/zero-item-time-fields` | Clear time fields on all items |
| POST | `/v1/actions/wipe-inventory` | Nuclear option (with options: wipeTags, wipeLocations, wipeMaintenance) |

---

## Label Maker (3 endpoints)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/label-maker/item/{id}` | Get printable item label |
| GET | `/v1/label-maker/asset/{id}` | Get asset label by asset ID |
| GET | `/v1/label-maker/location/{id}` | Get location label |

---

## Groups (10 endpoints), Notifiers (5), Users (8), Auth (5), Reporting (1)

Full CRUD on groups, members, invitations. Notifier webhooks. User management. Bill of materials export.

---

## MCP Server Tool Mapping

### High-value tools (implement first)
| MCP Tool | Homebox Endpoint | Description |
|----------|-----------------|-------------|
| `search_items` | GET /v1/items?q= | Natural language search |
| `get_item` | GET /v1/items/{id} | Full item details |
| `create_item` | POST /v1/items | Create new item |
| `update_item` | PUT /v1/items/{id} | Modify item |
| `list_locations` | GET /v1/locations/tree | Hierarchical location tree |
| `move_item` | PATCH /v1/items/{id} | Move item to location |
| `get_statistics` | GET /v1/groups/statistics | Inventory overview |
| `search_by_barcode` | GET /v1/assets/{id} | Barcode/asset lookup |
| `list_tags` | GET /v1/tags | All tags |
| `tag_item` | PATCH /v1/items/{id} | Add/remove tags |

### Medium-value tools
| MCP Tool | Homebox Endpoint | Description |
|----------|-----------------|-------------|
| `create_location` | POST /v1/locations | Add location |
| `create_tag` | POST /v1/tags | Add tag |
| `add_maintenance` | POST /v1/items/{id}/maintenance | Log maintenance |
| `get_location_items` | GET /v1/items?locations[]= | Items in a location |
| `export_inventory` | GET /v1/items/export | CSV export |
| `duplicate_item` | POST /v1/items/{id}/duplicate | Clone item |

### Low-value tools (nice to have)
| MCP Tool | Homebox Endpoint | Description |
|----------|-----------------|-------------|
| `upload_photo` | POST /v1/items/{id}/attachments | Add photo |
| `generate_label` | GET /v1/label-maker/item/{id} | Print label |
| `get_value_over_time` | GET /v1/groups/statistics/purchase-price | Value chart |
| `create_from_template` | POST /v1/templates/{id}/create-item | Template → item |
