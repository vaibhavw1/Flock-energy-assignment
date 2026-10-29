import httpx
from app.decoder import normalize_meter_details

from app.config import (
    PORTAL_BASE_URL,
    PORTAL_EMAIL,
    PORTAL_PASSWORD,
)


class PortalClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=PORTAL_BASE_URL,
            timeout=20.0,
            follow_redirects=True,
        )

    async def login(self):
        response = await self.client.post(
            "/login",
            data={
                "email": PORTAL_EMAIL,
                "password": PORTAL_PASSWORD,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": PORTAL_BASE_URL,
                "Referer": f"{PORTAL_BASE_URL}/login",
                "x-sveltekit-action": "true",
            },
        )

        print("LOGIN STATUS:", response.status_code)
        print(
            "SESSION COOKIE PRESENT:",
            "__Secure-better-auth.session_token" in self.client.cookies
        )

        response.raise_for_status()

        if "__Secure-better-auth.session_token" not in self.client.cookies:
            raise RuntimeError("Portal login did not establish a session")

    async def search_meters(self, query="", page=1):
        response = await self.client.get(
            "/portal/meters/search",
            params={
                "q": query,
                "page": page,
            },
        )

        print("SEARCH STATUS:", response.status_code)
        print("SEARCH CONTENT TYPE:", response.headers.get("content-type"))

        response.raise_for_status()

        return response.json()


    async def meter_exists(self, meter_id: str) -> bool:
        result = await self.search_meters(query=meter_id, page=1)

        return any(
            str(meter.get("meterId", "")).lower() == meter_id.lower()
            for meter in result.get("data", [])
        )

    async def get_meter_location(self, meter_id: str):
        response = await self.client.get(
            f"/portal/meters/{meter_id}/geo"
        )

        response.raise_for_status()
        return response.json()


    async def get_meter_energy(self, meter_id: str):
        response = await self.client.get(
            f"/portal/meters/{meter_id}/energy"
        )

        response.raise_for_status()
        return response.json()
    async def get_meter_details(self, meter_id: str):
        response = await self.client.get(
            f"/meters/{meter_id}/__data.json",
            params={
                "x-sveltekit-invalidated": "001"
            },
        )

        print("METER DETAILS STATUS:", response.status_code)
        print(
            "METER DETAILS CONTENT TYPE:",
            response.headers.get("content-type")
        )

        response.raise_for_status()

        result = response.json()

        print("RESPONSE TYPE:", result.get("type"))
        print("NODE TYPES:", [
            node.get("type")
            for node in result.get("nodes", [])
        ])

        return normalize_meter_details(result)

    async def close(self):
        await self.client.aclose()