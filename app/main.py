from fastapi import FastAPI
import httpx

from fastapi import HTTPException, Query
from app.client import PortalClient

app = FastAPI(
    title="Flock Energy Meter API",
    description="REST API for accessing Urja Meter Ops data",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "flock-energy-meter-api"
    }

@app.get("/api/v1/meters")
async def get_meters(
    q: str = "",
    page: int = Query(default=1, ge=1),
):
    portal = PortalClient()

    try:
        await portal.login()

        result = await portal.search_meters(
            query=q,
            page=page,
        )

        return result

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream portal returned HTTP {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with the portal",
        )

    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail="Portal authentication failed",
        )

    finally:
        await portal.close()

@app.get("/api/v1/meters/{meter_id}/location")
async def get_meter_location(meter_id: str):
    portal = PortalClient()

    try:
        await portal.login()
        return await portal.get_meter_location(meter_id)


    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Meter '{meter_id}' not found"
            )

        raise HTTPException(
            status_code=502,
            detail=f"Upstream portal returned HTTP {exc.response.status_code}"
        )

    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail="Portal authentication failed"
        )

    finally:
        await portal.close()


@app.get("/api/v1/meters/{meter_id}/energy")
async def get_meter_energy(meter_id: str):
    portal = PortalClient()

    try:
        await portal.login()
        return await portal.get_meter_energy(meter_id)

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Meter '{meter_id}' not found"
            )

        raise HTTPException(
            status_code=502,
            detail=f"Upstream portal returned HTTP {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with the portal"
        )

    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail="Portal authentication failed"
        )

    finally:
        await portal.close()

@app.get("/api/v1/meters/{meter_id}")
async def get_meter_details(meter_id: str):
    portal = PortalClient()

    try:
        await portal.login()

        return await portal.get_meter_details(meter_id)

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream portal returned HTTP {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with the portal"
        )

    except (RuntimeError, ValueError, KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="Unable to authenticate or decode portal response"
        )

    finally:
        await portal.close()