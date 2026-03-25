"""Homebox MCP Server — inventory management via natural language.

Exposes the Homebox REST API as MCP tools for AI agents.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from client import HomeboxClient, HomeboxError

# ── Server & client setup ────────────────────────────────────────────

mcp = FastMCP(
    "homebox",
    instructions=(
        "Homebox inventory management server. Use these tools to search, "
        "create, update, move, and delete inventory items, locations, and "
        "tags in a Homebox instance. All IDs are UUIDs."
    ),
)

hb = HomeboxClient()


# ── Parsing helpers ──────────────────────────────────────────────────

def _parse_csv_ids(s: str) -> list[str]:
    """Split a comma-separated string of IDs, stripping whitespace."""
    return [t.strip() for t in s.split(",") if t.strip()]


# ── Formatting helpers ───────────────────────────────────────────────

def _fmt_item_summary(item: dict) -> str:
    """One-line summary of an item."""
    parts = [f"- {item.get('name', '?')}"]
    if item.get("quantity", 1) > 1:
        parts.append(f"(qty: {item['quantity']})")
    loc = item.get("location")
    if loc:
        parts.append(f"@ {loc.get('name', '?')}")
    if item.get("tags"):
        tag_names = ", ".join(t.get("name", "?") for t in item["tags"])
        parts.append(f"[{tag_names}]")
    if item.get("id"):
        parts.append(f"  id:{item['id']}")
    return " ".join(parts)


def _fmt_item_detail(item: dict) -> str:
    """Full detail block for a single item."""
    lines = [
        f"Name: {item.get('name', '?')}",
        f"ID: {item.get('id', '?')}",
    ]
    if item.get("description"):
        lines.append(f"Description: {item['description']}")
    lines.append(f"Quantity: {item.get('quantity', 1)}")

    loc = item.get("location")
    if loc:
        lines.append(f"Location: {loc.get('name', '?')} (id:{loc.get('id', '?')})")

    if item.get("tags"):
        tag_str = ", ".join(
            f"{t.get('name', '?')} (id:{t.get('id', '?')})" for t in item["tags"]
        )
        lines.append(f"Tags: {tag_str}")

    for field_name, key in [
        ("Manufacturer", "manufacturer"),
        ("Model", "modelNumber"),
        ("Serial", "serialNumber"),
        ("Asset ID", "assetId"),
        ("Purchase Price", "purchasePrice"),
        ("Purchase From", "purchaseFrom"),
        ("Notes", "notes"),
    ]:
        val = item.get(key)
        if val:
            if key == "purchasePrice":
                lines.append(f"{field_name}: ${val}")
            else:
                lines.append(f"{field_name}: {val}")

    if item.get("warrantyExpires"):
        lines.append(f"Warranty Expires: {item['warrantyExpires']}")
    if item.get("lifetimeWarranty"):
        lines.append("Warranty: Lifetime")

    if item.get("fields"):
        lines.append("Custom Fields:")
        for f in item["fields"]:
            val = f.get("textValue") or f.get("numberValue") or f.get("booleanValue")
            lines.append(f"  {f.get('name', '?')}: {val}")

    if item.get("attachments"):
        lines.append(f"Attachments: {len(item['attachments'])} file(s)")
        for a in item["attachments"]:
            atype = a.get("type", "attachment")
            lines.append(f"  - [{atype}] id:{a.get('id', '?')}")

    if item.get("insured"):
        lines.append("Insured: Yes")
    if item.get("archived"):
        lines.append("Archived: Yes")

    return "\n".join(lines)


def _fmt_location(loc: dict, indent: int = 0) -> str:
    """Format a location with optional indentation for tree display."""
    prefix = "  " * indent
    count = loc.get("itemCount", 0)
    price = loc.get("totalPrice", 0)
    line = f"{prefix}- {loc.get('name', '?')} ({count} items"
    if price:
        line += f", ${price:.2f}"
    line += f")  id:{loc.get('id', '?')}"
    return line


def _fmt_location_tree(locations: list[dict], indent: int = 0) -> list[str]:
    """Recursively format a location tree."""
    lines: list[str] = []
    for loc in locations:
        lines.append(_fmt_location(loc, indent))
        children = loc.get("children") or []
        if children:
            lines.extend(_fmt_location_tree(children, indent + 1))
    return lines


# ── MCP Tools ────────────────────────────────────────────────────────

@mcp.tool(description="Search and list inventory items. Supports text search, location filtering, and tag filtering. Returns paginated results.")
async def search_items(
    query: str = "",
    location_id: str = "",
    tag_ids: str = "",
    page: int = 1,
    page_size: int = 25,
) -> str:
    """Search inventory items.

    Args:
        query: Search text (matches name, description, fields).
        location_id: Filter to a specific location UUID.
        tag_ids: Comma-separated tag UUIDs to filter by.
        page: Page number (starts at 1).
        page_size: Results per page (max 100).
    """
    try:
        loc_ids = [location_id] if location_id else None
        t_ids = _parse_csv_ids(tag_ids) if tag_ids else None
        data = await hb.search_items(
            query=query,
            location_ids=loc_ids,
            tag_ids=t_ids,
            page=page,
            page_size=min(page_size, 100),
        )
        items = data.get("items") or []
        total = data.get("total", len(items))

        if not items:
            search_desc = f" for '{query}'" if query else ""
            return f"No items found{search_desc}."

        lines = [f"Found {total} item(s) (page {page}, showing {len(items)}):"]
        lines.append("")
        for item in items:
            lines.append(_fmt_item_summary(item))

        if total > page * page_size:
            lines.append(f"\n... {total - page * page_size} more items. Use page={page + 1} to see next page.")

        return "\n".join(lines)
    except HomeboxError as e:
        return f"Error searching items: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Get full details of a single inventory item including all fields, attachments, location, and tags.")
async def get_item(id: str) -> str:
    """Get complete item details.

    Args:
        id: Item UUID.
    """
    try:
        item = await hb.get_item(id)
        return _fmt_item_detail(item)
    except HomeboxError as e:
        return f"Error getting item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Create a new inventory item. Returns the created item details.")
async def create_item(
    name: str,
    description: str = "",
    location_id: str = "",
    quantity: int = 1,
    tag_ids: str = "",
) -> str:
    """Create a new item.

    Args:
        name: Item name (required, 1-255 chars).
        description: Item description (max 1000 chars).
        location_id: UUID of location to place item in.
        quantity: How many of this item (default 1).
        tag_ids: Comma-separated tag UUIDs to apply.
    """
    try:
        payload: dict = {"name": name, "quantity": quantity}
        if description:
            payload["description"] = description
        if location_id:
            payload["locationId"] = location_id
        if tag_ids:
            payload["tagIds"] = _parse_csv_ids(tag_ids)

        item = await hb.create_item(payload)
        return f"Item created successfully.\n\n{_fmt_item_detail(item)}"
    except HomeboxError as e:
        return f"Error creating item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Update an existing item. Fetches current state, merges your changes, and saves. Only specify fields you want to change.")
async def update_item(
    id: str,
    name: str = "",
    description: str = "",
    location_id: str = "",
    quantity: int | None = None,
    manufacturer: str = "",
    model_number: str = "",
    serial_number: str = "",
    purchase_price: float | None = None,
    notes: str = "",
) -> str:
    """Update an item (merge-style: only changed fields are modified).

    Args:
        id: Item UUID (required).
        name: New name (leave empty to keep current).
        description: New description (leave empty to keep current).
        location_id: New location UUID (leave empty to keep current).
        quantity: New quantity (omit to keep current).
        manufacturer: Manufacturer name.
        model_number: Model number.
        serial_number: Serial number.
        purchase_price: Price paid (omit to keep current).
        notes: Notes text.
    """
    try:
        # Fetch current item state
        current = await hb.get_item(id)

        # Build update payload from current state
        update: dict = {
            "id": id,
            "name": current.get("name", ""),
            "description": current.get("description", ""),
            "quantity": current.get("quantity", 1),
            "insured": current.get("insured", False),
            "archived": current.get("archived", False),
            "assetId": current.get("assetId", ""),
            "manufacturer": current.get("manufacturer", ""),
            "modelNumber": current.get("modelNumber", ""),
            "serialNumber": current.get("serialNumber", ""),
            "purchasePrice": current.get("purchasePrice", 0),
            "purchaseFrom": current.get("purchaseFrom", ""),
            "purchaseTime": current.get("purchaseTime", ""),
            "soldPrice": current.get("soldPrice", 0),
            "soldTo": current.get("soldTo", ""),
            "soldNotes": current.get("soldNotes", ""),
            "soldTime": current.get("soldTime", ""),
            "warrantyExpires": current.get("warrantyExpires", ""),
            "warrantyDetails": current.get("warrantyDetails", ""),
            "lifetimeWarranty": current.get("lifetimeWarranty", False),
            "notes": current.get("notes", ""),
            "syncChildItemsLocations": current.get("syncChildItemsLocations", False),
        }

        # Location
        loc = current.get("location")
        if loc:
            update["locationId"] = loc.get("id", "")
        else:
            update["locationId"] = ""

        # Tags
        tags = current.get("tags") or []
        update["tagIds"] = [t["id"] for t in tags if "id" in t]

        # Fields
        update["fields"] = current.get("fields") or []

        # Apply requested changes
        if name:
            update["name"] = name
        if description:
            update["description"] = description
        if location_id:
            update["locationId"] = location_id
        if quantity is not None:
            update["quantity"] = quantity
        if manufacturer:
            update["manufacturer"] = manufacturer
        if model_number:
            update["modelNumber"] = model_number
        if serial_number:
            update["serialNumber"] = serial_number
        if purchase_price is not None:
            update["purchasePrice"] = purchase_price
        if notes:
            update["notes"] = notes

        result = await hb.update_item(id, update)
        return f"Item updated successfully.\n\n{_fmt_item_detail(result)}"
    except HomeboxError as e:
        return f"Error updating item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Move an item to a different location.")
async def move_item(id: str, location_id: str) -> str:
    """Move an item to a new location using PATCH.

    Args:
        id: Item UUID.
        location_id: Target location UUID.
    """
    try:
        # GET current to preserve quantity and tags
        current = await hb.get_item(id)
        tags = current.get("tags") or []
        tag_ids = [t["id"] for t in tags if "id" in t]

        patch_data = {
            "id": id,
            "locationId": location_id,
            "quantity": current.get("quantity", 1),
            "tagIds": tag_ids,
        }
        result = await hb.patch_item(id, patch_data)

        loc_name = location_id
        # Try to resolve location name
        try:
            loc = await hb.get_location(location_id)
            loc_name = loc.get("name", location_id)
        except Exception:
            pass

        return f"Moved '{current.get('name', '?')}' to '{loc_name}'."
    except HomeboxError as e:
        return f"Error moving item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="List all locations in the inventory, showing item counts and hierarchy.")
async def list_locations() -> str:
    """Get all locations with item counts and total values."""
    try:
        # Try tree first for hierarchy
        try:
            tree = await hb.get_location_tree()
            if tree:
                lines = ["Locations (hierarchical):"]
                lines.append("")
                lines.extend(_fmt_location_tree(tree))
                return "\n".join(lines)
        except Exception:
            pass

        # Fallback to flat list
        locations = await hb.list_locations()
        if not locations:
            return "No locations found."

        lines = [f"Locations ({len(locations)} total):"]
        lines.append("")
        for loc in locations:
            lines.append(_fmt_location(loc))
        return "\n".join(lines)
    except HomeboxError as e:
        return f"Error listing locations: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Get details of a specific location including its children and items.")
async def get_location(id: str) -> str:
    """Get location details with children and items.

    Args:
        id: Location UUID.
    """
    try:
        loc = await hb.get_location(id)
        lines = [
            f"Name: {loc.get('name', '?')}",
            f"ID: {loc.get('id', '?')}",
        ]
        if loc.get("description"):
            lines.append(f"Description: {loc['description']}")

        parent = loc.get("parent")
        if parent:
            lines.append(f"Parent: {parent.get('name', '?')} (id:{parent.get('id', '?')})")

        lines.append(f"Items: {loc.get('itemCount', 0)}")
        price = loc.get("totalPrice", 0)
        if price:
            lines.append(f"Total Value: ${price:.2f}")

        children = loc.get("children") or []
        if children:
            lines.append(f"\nChild locations ({len(children)}):")
            for child in children:
                lines.append(_fmt_location(child, indent=1))

        # Also fetch items at this location
        try:
            items_data = await hb.search_items(location_ids=[id], page_size=50)
            items = items_data.get("items") or []
            if items:
                lines.append(f"\nItems at this location ({len(items)}):")
                for item in items:
                    lines.append(_fmt_item_summary(item))
        except Exception:
            pass

        return "\n".join(lines)
    except HomeboxError as e:
        return f"Error getting location: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Create a new location. Optionally nest it under a parent location.")
async def create_location(
    name: str,
    description: str = "",
    parent_id: str = "",
) -> str:
    """Create a new location.

    Args:
        name: Location name (required).
        description: Location description.
        parent_id: Parent location UUID (for nesting).
    """
    try:
        payload: dict = {"name": name}
        if description:
            payload["description"] = description
        if parent_id:
            payload["parentId"] = parent_id

        loc = await hb.create_location(payload)
        result = f"Location created: {loc.get('name', '?')} (id:{loc.get('id', '?')})"
        if parent_id:
            result += f"\nParent: {parent_id}"
        return result
    except HomeboxError as e:
        return f"Error creating location: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="List all tags in the inventory.")
async def list_tags() -> str:
    """Get all tags with their IDs."""
    try:
        tags = await hb.list_tags()
        if not tags:
            return "No tags found."

        lines = [f"Tags ({len(tags)} total):"]
        lines.append("")
        for tag in tags:
            parts = [f"- {tag.get('name', '?')}"]
            if tag.get("color"):
                parts.append(f"({tag['color']})")
            if tag.get("description"):
                parts.append(f"— {tag['description']}")
            parts.append(f"  id:{tag.get('id', '?')}")
            lines.append(" ".join(parts))
        return "\n".join(lines)
    except HomeboxError as e:
        return f"Error listing tags: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Create a new tag for categorizing items.")
async def create_tag(
    name: str,
    description: str = "",
    color: str = "",
) -> str:
    """Create a new tag.

    Args:
        name: Tag name (required).
        description: Tag description.
        color: Hex color (e.g. '#ff0000').
    """
    try:
        payload: dict = {"name": name}
        if description:
            payload["description"] = description
        if color:
            payload["color"] = color

        tag = await hb.create_tag(payload)
        return f"Tag created: {tag.get('name', '?')} (id:{tag.get('id', '?')})"
    except HomeboxError as e:
        return f"Error creating tag: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Set tags on an item. Replaces all existing tags with the specified ones.")
async def tag_item(item_id: str, tag_ids: str) -> str:
    """Set tags on an item (replaces existing tags).

    Args:
        item_id: Item UUID.
        tag_ids: Comma-separated tag UUIDs to set.
    """
    try:
        current = await hb.get_item(item_id)
        parsed_tags = _parse_csv_ids(tag_ids)

        patch_data = {
            "id": item_id,
            "locationId": current.get("location", {}).get("id", ""),
            "quantity": current.get("quantity", 1),
            "tagIds": parsed_tags,
        }
        await hb.patch_item(item_id, patch_data)

        # Resolve tag names for confirmation
        tag_names: list[str] = []
        try:
            all_tags = await hb.list_tags()
            tag_map = {t["id"]: t.get("name", "?") for t in all_tags}
            tag_names = [tag_map.get(tid, tid) for tid in parsed_tags]
        except Exception:
            tag_names = parsed_tags

        item_name = current.get("name", "?")
        if tag_names:
            return f"Set tags on '{item_name}': {', '.join(tag_names)}"
        else:
            return f"Cleared all tags from '{item_name}'."
    except HomeboxError as e:
        return f"Error tagging item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Get inventory statistics overview: total items, locations, tags, total value.")
async def get_statistics() -> str:
    """Get overall inventory statistics."""
    try:
        stats = await hb.get_statistics()
        lines = [
            "Inventory Statistics:",
            "",
            f"Total Items: {stats.get('totalItems', 0)}",
            f"Total Locations: {stats.get('totalLocations', 0)}",
            f"Total Tags: {stats.get('totalTags', 0)}",
            f"Total Users: {stats.get('totalUsers', 0)}",
            f"Total Value: ${stats.get('totalItemPrice', 0):.2f}",
            f"Items with Warranty: {stats.get('totalWithWarranty', 0)}",
        ]

        # Try to get per-location breakdown
        try:
            loc_stats = await hb.get_location_statistics()
            if loc_stats:
                lines.append("\nValue by Location:")
                for ls in loc_stats:
                    lines.append(
                        f"  - {ls.get('name', '?')}: "
                        f"{ls.get('itemCount', 0)} items, "
                        f"${ls.get('totalPrice', 0):.2f}"
                    )
        except Exception:
            pass

        return "\n".join(lines)
    except HomeboxError as e:
        return f"Error getting statistics: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Look up an item by its asset ID (barcode number). Asset IDs are numeric identifiers printed on labels.")
async def search_by_barcode(barcode: str) -> str:
    """Look up an item by asset ID / barcode.

    Args:
        barcode: Asset ID string (usually numeric, e.g. '000-001').
    """
    try:
        item = await hb.get_item_by_asset_id(barcode)
        return _fmt_item_detail(item)
    except HomeboxError as e:
        if e.status == 404:
            return f"No item found with asset ID '{barcode}'."
        return f"Error looking up barcode: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Log a maintenance entry for an item (repairs, cleaning, inspections, etc).")
async def add_maintenance(
    item_id: str,
    name: str,
    description: str = "",
    cost: float = 0,
    scheduled_date: str = "",
    completed_date: str = "",
) -> str:
    """Add a maintenance record to an item.

    Args:
        item_id: Item UUID.
        name: Maintenance task name (e.g. 'Oil change', 'Filter replaced').
        description: Detailed description of the work.
        cost: Cost of maintenance.
        scheduled_date: When it's scheduled (ISO date, e.g. '2025-06-15').
        completed_date: When it was completed (ISO date).
    """
    try:
        payload: dict = {"name": name}
        if description:
            payload["description"] = description
        if cost > 0:
            payload["cost"] = cost
        if scheduled_date:
            payload["scheduledDate"] = scheduled_date
        if completed_date:
            payload["completedDate"] = completed_date

        entry = await hb.create_maintenance(item_id, payload)

        # Get item name for confirmation
        item_name = item_id
        try:
            item = await hb.get_item(item_id)
            item_name = item.get("name", item_id)
        except Exception:
            pass

        result = f"Maintenance logged for '{item_name}': {name}"
        if cost > 0:
            result += f" (${cost:.2f})"
        if entry.get("id"):
            result += f"\nEntry ID: {entry['id']}"
        return result
    except HomeboxError as e:
        return f"Error adding maintenance: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool(description="Permanently delete an item from inventory. This cannot be undone.")
async def delete_item(id: str) -> str:
    """Delete an item.

    Args:
        id: Item UUID to delete.
    """
    try:
        # Get item name before deleting for confirmation
        item_name = id
        try:
            item = await hb.get_item(id)
            item_name = item.get("name", id)
        except Exception:
            pass

        await hb.delete_item(id)
        return f"Deleted item: '{item_name}' (id:{id})"
    except HomeboxError as e:
        return f"Error deleting item: {e.detail}"
    except Exception as e:
        return f"Error: {e}"


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
