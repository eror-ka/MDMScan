from __future__ import annotations

import aiohttp

from app.config import settings


async def submit_scan(image: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{settings.api_url}/scans",
            json={"image": image},
        ) as r:
            r.raise_for_status()
            return await r.json()


async def get_scan(scan_id: str) -> dict | None:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{settings.api_url}/scans/{scan_id}") as r:
            if r.status == 404:
                return None
            r.raise_for_status()
            return await r.json()


async def get_findings(
    scan_id: str,
    severity: str | None = None,
    category: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    params: list[str] = [f"limit={limit}", f"offset={offset}"]
    if severity:
        params.append(f"severity={severity}")
    if category:
        params.append(f"category={category}")
    query = "&".join(params)
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{settings.api_url}/scans/{scan_id}/findings?{query}") as r:
            r.raise_for_status()
            return await r.json()


async def delete_scan(scan_id: str) -> None:
    async with aiohttp.ClientSession() as s:
        async with s.delete(f"{settings.api_url}/scans/{scan_id}") as r:
            r.raise_for_status()


async def list_scans(limit: int = 5, offset: int = 0) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{settings.api_url}/scans?limit={limit}&offset={offset}"
        ) as r:
            r.raise_for_status()
            return await r.json()
