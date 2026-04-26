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


async def get_findings(scan_id: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{settings.api_url}/scans/{scan_id}/findings?limit=500") as r:
            r.raise_for_status()
            return await r.json()


async def list_scans(limit: int = 5) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{settings.api_url}/scans?limit={limit}") as r:
            r.raise_for_status()
            return await r.json()
