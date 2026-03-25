"""Homebox API client — typed wrapper around the REST API."""

from __future__ import annotations

import httpx
import os
from typing import Any

HOMEBOX_URL = os.environ.get("HOMEBOX_URL", "http://192.168.42.99:3100")
HOMEBOX_TOKEN = os.environ.get("HOMEBOX_TOKEN", "")


class HomeboxError(Exception):
    """Raised when a Homebox API call fails."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"Homebox API error {status}: {detail}")


class HomeboxClient:
    """Async client for the Homebox REST API (v1)."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or HOMEBOX_URL).rstrip("/")
        self.token = token or HOMEBOX_TOKEN
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def _request(
        self,
        method: str,
        path: str,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an HTTP request against the Homebox API.

        Returns the parsed JSON response body.  For 204 No Content
        responses (e.g. DELETE), returns None.
        """
        url = f"{self.base_url}/api/v1{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.request(
                method,
                url,
                headers=self._headers(),
                json=json,
                params=params,
            )
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HomeboxError(resp.status_code, str(detail))
        if resp.status_code == 204:
            return None
        return resp.json()

    # ── Items ────────────────────────────────────────────────────────

    async def search_items(
        self,
        query: str = "",
        location_ids: list[str] | None = None,
        tag_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        params: dict[str, Any] = {"q": query, "page": page, "pageSize": page_size}
        if location_ids:
            for lid in location_ids:
                params.setdefault("locations[]", [])
                if isinstance(params["locations[]"], list):
                    params["locations[]"].append(lid)
                else:
                    params["locations[]"] = [params["locations[]"], lid]
        if tag_ids:
            for tid in tag_ids:
                params.setdefault("tags[]", [])
                if isinstance(params["tags[]"], list):
                    params["tags[]"].append(tid)
                else:
                    params["tags[]"] = [params["tags[]"], tid]
        return await self._request("GET", "/items", params=params)

    async def get_item(self, item_id: str) -> dict:
        return await self._request("GET", f"/items/{item_id}")

    async def create_item(self, data: dict) -> dict:
        return await self._request("POST", "/items", json=data)

    async def update_item(self, item_id: str, data: dict) -> dict:
        return await self._request("PUT", f"/items/{item_id}", json=data)

    async def patch_item(self, item_id: str, data: dict) -> dict:
        return await self._request("PATCH", f"/items/{item_id}", json=data)

    async def delete_item(self, item_id: str) -> None:
        await self._request("DELETE", f"/items/{item_id}")

    async def get_item_by_asset_id(self, asset_id: str) -> dict:
        return await self._request("GET", f"/assets/{asset_id}")

    # ── Locations ────────────────────────────────────────────────────

    async def list_locations(self) -> list[dict]:
        return await self._request("GET", "/locations")

    async def get_location_tree(self) -> list[dict]:
        return await self._request("GET", "/locations/tree")

    async def get_location(self, location_id: str) -> dict:
        return await self._request("GET", f"/locations/{location_id}")

    async def create_location(self, data: dict) -> dict:
        return await self._request("POST", "/locations", json=data)

    # ── Tags ─────────────────────────────────────────────────────────

    async def list_tags(self) -> list[dict]:
        return await self._request("GET", "/tags")

    async def create_tag(self, data: dict) -> dict:
        return await self._request("POST", "/tags", json=data)

    # ── Maintenance ──────────────────────────────────────────────────

    async def list_maintenance(self, item_id: str) -> list[dict]:
        return await self._request("GET", f"/items/{item_id}/maintenance")

    async def create_maintenance(self, item_id: str, data: dict) -> dict:
        return await self._request("POST", f"/items/{item_id}/maintenance", json=data)

    # ── Statistics ───────────────────────────────────────────────────

    async def get_statistics(self) -> dict:
        return await self._request("GET", "/groups/statistics")

    async def get_location_statistics(self) -> list[dict]:
        return await self._request("GET", "/groups/statistics/locations")

    async def get_tag_statistics(self) -> list[dict]:
        return await self._request("GET", "/groups/statistics/tags")
