# Flock Energy Meter API

A small FastAPI service built on top of the Urja Meter Ops portal to access meter information through REST endpoints.

The portal uses session-based authentication, and some of its responses are in SvelteKit's serialized format. This project handles those details and exposes the data as JSON.
Before fetching meter details, the API checks whether the meter ID exists using the portal's search endpoint. If the meter is not found, it returns 404.

## Tech Stack

- Python, FastAPI
- HTTPX for portal requests
- pytest for testing
- python-dotenv for configuration

## Setup

Clone the repository and install the dependencies.

```bash
git clone <repository-url>
cd flock-energy-assignment

python -m venv venv
```

Activate the virtual environment (Windows):

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory:

```env
PORTAL_BASE_URL=https://urja-ops.flockenergy.tech
PORTAL_EMAIL=your_email
PORTAL_PASSWORD=your_password
```

Start the server:

```bash
uvicorn app.main:app --reload
```

Swagger documentation is available at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/meters` | List/search meters |
| GET | `/api/v1/meters/{meter_id}` | Meter details and hierarchy |
| GET | `/api/v1/meters/{meter_id}/location` | Meter coordinates |
| GET | `/api/v1/meters/{meter_id}/energy` | Energy readings |

Search supports `q` and `page` parameters.

Example:

```http
GET /api/v1/meters?q=J100001&page=1
```

## How It Works

The API authenticates with the portal using the configured credentials. HTTPX maintains the session cookie for subsequent requests.

The code is split into a few files:

- `main.py` — FastAPI routes and error handling.
- `client.py` — Login and requests to the portal.
- `decoder.py` — Decodes SvelteKit data returned by the meter details page.
- `config.py` — Loads environment variables.

For meter details, the portal returns indexed data instead of regular nested JSON. The decoder resolves these references and extracts meter information and network hierarchy.

## Design Decisions and Trade-offs

I used FastAPI and HTTPX because the main requirement was to build a simple API that communicates with the existing portal.

I decided to fetch data directly from the portal instead of storing it locally. This keeps the data current and avoids maintaining a separate database, but it also means the API depends on the portal being available.

For now, each request creates a new session and logs in again. This was easier to implement and test, although reusing sessions would reduce unnecessary login requests.

I also kept the SvelteKit decoding logic separate from the API routes because the response format is specific to the portal.

## Testing

Run:

```bash
python -m pytest -v
```

The tests use mocked portal responses, so they don't require a live connection.

The OpenAPI specification is included in `openapi.json`.

## Assumptions and Scope

I assumed the portal's endpoints and response formats would remain consistent with what I observed during testing. I also kept the original measurement values and timestamps rather than converting them into different formats.

I focused on meter search, details, hierarchy, location, and energy readings. I did not add a frontend, caching, local indexing, or bulk data extraction because these were outside the core requirements.

## Limitations

- Currently, a new login is performed for each API request.
- The implementation depends on the portal's existing endpoints and response format.
- No caching or database is implemented.

With more time, I would improve session reuse, error handling, and response validation.

For Portal investigation , see `PROTOCOL.md`. My implementation notes and reflection are in `REFLECTION.md`.
The generated API specification is available in `openapi.json`.