# Homebox MCP Server

MCP (Model Context Protocol) server that exposes the Homebox inventory API as tools for AI agents.

## Tools

| Tool | Description |
|------|-------------|
| `search_items` | Search/filter inventory items by text, location, or tags |
| `get_item` | Get full item details (fields, attachments, location, tags) |
| `create_item` | Create a new inventory item |
| `update_item` | Update item fields (merge-style, only changed fields) |
| `move_item` | Move an item to a different location |
| `delete_item` | Permanently delete an item |
| `list_locations` | List all locations with item counts (hierarchical) |
| `get_location` | Get location details with children and items |
| `create_location` | Create a new location (optionally nested) |
| `list_tags` | List all tags |
| `create_tag` | Create a new tag |
| `tag_item` | Set tags on an item |
| `get_statistics` | Inventory overview (totals, value by location) |
| `search_by_barcode` | Look up item by asset ID |
| `add_maintenance` | Log a maintenance entry on an item |

## Setup

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOMEBOX_URL` | No | `http://192.168.42.99:3100` | Homebox instance URL |
| `HOMEBOX_TOKEN` | Yes | — | Bearer token for API auth |

### Get a Bearer Token

Log into Homebox, then grab a token from the API:

```bash
curl -s -X POST http://192.168.42.99:3100/api/v1/users/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "you@example.com", "password": "yourpassword"}' \
  | jq -r '.token'
```

Or use a long-lived API key from Homebox Settings > API Keys.

### Run Locally (stdio)

```bash
cd mcp-server
pip install -r requirements.txt

export HOMEBOX_URL=http://192.168.42.99:3100
export HOMEBOX_TOKEN=your-bearer-token

python server.py
```

### Run via Docker

```bash
docker build -t homebox-mcp ./mcp-server

docker run --rm \
  -e HOMEBOX_URL=http://192.168.42.99:3100 \
  -e HOMEBOX_TOKEN=your-bearer-token \
  homebox-mcp
```

## Agent Registration

### Claude Code

Add to `~/.claude/settings.json` (or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "homebox": {
      "command": "python",
      "args": ["/home/sheep/homebox-ai-studio/mcp-server/server.py"],
      "env": {
        "HOMEBOX_URL": "http://192.168.42.99:3100",
        "HOMEBOX_TOKEN": "your-bearer-token"
      }
    }
  }
}
```

### OpenClaw

Add to `~/.openclaw/openclaw.json` in the `mcpServers` section:

```json
{
  "mcpServers": {
    "homebox": {
      "command": "python",
      "args": ["/home/sheep/homebox-ai-studio/mcp-server/server.py"],
      "env": {
        "HOMEBOX_URL": "http://192.168.42.99:3100",
        "HOMEBOX_TOKEN": "your-bearer-token"
      }
    }
  }
}
```

### Docker Compose (Studio Stack)

Add this service to `docker/docker-compose.studio.yml`:

```yaml
  homebox-mcp:
    build: ../mcp-server
    container_name: homebox-mcp
    restart: always
    environment:
      - HOMEBOX_URL=http://homebox:7745
      - HOMEBOX_TOKEN=${HOMEBOX_MCP_TOKEN}
    stdin_open: true
```

Note: When running inside the Docker network, use `http://homebox:7745` as the URL
(the internal port, not the published one).

## Architecture

```
mcp-server/
  __init__.py          # Package marker
  server.py            # MCP server — all 15 tools, formatting, entry point
  client.py            # Homebox API client — typed async wrapper
  requirements.txt     # mcp, httpx
  Dockerfile           # Container image
  README.md            # This file
```

The server uses the FastMCP high-level API from the `mcp` SDK. Each tool is a
decorated async function that calls the Homebox REST API via `client.py` and
returns human-readable text (not raw JSON) suitable for LLM consumption.
