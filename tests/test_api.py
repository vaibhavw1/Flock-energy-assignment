import pytest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_invalid_page():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/meters?page=0")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_meter_search():
    mock_result = {
        "data": [
            {
                "meterId": "J100001",
                "serialNo": "GE84132",
                "make": "L&T",
                "phaseType": "single",
                "installStatus": "Installed",
                "dtCode": "DT-002"
            }
        ],
        "total": 1,
        "page": 1,
        "pageSize": 20
    }

    with patch("app.main.PortalClient") as mock_portal_class:
        mock_portal = mock_portal_class.return_value

        mock_portal.login = AsyncMock()
        mock_portal.search_meters = AsyncMock(
            return_value=mock_result
        )
        mock_portal.close = AsyncMock()

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/meters?q=J100001&page=1"
            )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["data"][0]["meterId"] == "J100001"

    mock_portal.login.assert_awaited_once()
    mock_portal.search_meters.assert_awaited_once_with(
        query="J100001",
        page=1
    )
    mock_portal.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_meter_location():
    mock_result = {
        "data": {
            "latitude": "26.938961002479868",
            "longitude": "75.83095696146852"
        }
    }

    with patch("app.main.PortalClient") as mock_portal_class:
        mock_portal = mock_portal_class.return_value

        mock_portal.login = AsyncMock()
        mock_portal.get_meter_location = AsyncMock(
            return_value=mock_result
        )
        mock_portal.close = AsyncMock()

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/meters/J100000/location"
            )

    assert response.status_code == 200
    assert response.json()["data"]["latitude"] == (
        "26.938961002479868"
    )


@pytest.mark.asyncio
async def test_meter_energy():
    mock_result = {
        "data": [
            {
                "timestamp": "23/06/2026 23:30",
                "kwh": "48438.74",
                "kvah": "52313.84",
                "voltR": "226"
            }
        ]
    }

    with patch("app.main.PortalClient") as mock_portal_class:
        mock_portal = mock_portal_class.return_value

        mock_portal.login = AsyncMock()
        mock_portal.get_meter_energy = AsyncMock(
            return_value=mock_result
        )
        mock_portal.close = AsyncMock()

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/meters/J100000/energy"
            )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["kwh"] == "48438.74"


@pytest.mark.asyncio
async def test_meter_details():
    mock_result = {
        "meterId": "J100001",
        "details": {
            "Meter ID": "J100001",
            "Make": "L&T",
            "Installation Status": "Installed"
        },
        "hierarchy": {
            "Zone": "Jaipur Zone 2 (Z-02)",
            "Circle": "Circle 2 (C-02)"
        }
    }

    with patch("app.main.PortalClient") as mock_portal_class:
        mock_portal = mock_portal_class.return_value

        mock_portal.login = AsyncMock()
        mock_portal.meter_exists = AsyncMock(return_value=True)
        mock_portal.get_meter_details = AsyncMock(
            return_value=mock_result
        )
        mock_portal.close = AsyncMock()

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/meters/J100001"
            )

    assert response.status_code == 200
    assert response.json()["meterId"] == "J100001"
    assert response.json()["details"]["Make"] == "L&T"
    assert "Zone" in response.json()["hierarchy"]


@pytest.mark.asyncio
async def test_meter_not_found():
    with patch("app.main.PortalClient") as mock_portal_class:
        mock_portal = mock_portal_class.return_value

        mock_portal.login = AsyncMock()
        mock_portal.get_meter_details = AsyncMock(
            side_effect=ValueError("Invalid meter response")
        )
        mock_portal.close = AsyncMock()

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/meters/INVALID123"
            )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to authenticate or decode portal response"
    )