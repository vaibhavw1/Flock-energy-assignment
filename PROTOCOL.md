# Portal Protocol Notes

These are the endpoints and request patterns I found while inspecting the Urja Meter Ops portal using Chrome DevTools.

The portal uses SvelteKit, so not every response is normal JSON. I used HTTPX to reproduce the requests in Python.

## 1. Login

**Endpoint:** `POST /login`

The login request sends email and password as form data (`application/x-www-form-urlencoded`).

Some headers were needed to reproduce the browser request:

```http
Accept: application/json
Content-Type: application/x-www-form-urlencoded
Origin: https://urja-ops.flockenergy.tech
Referer: https://urja-ops.flockenergy.tech/login
x-sveltekit-action: true
```

After a successful login, the response contains a redirect to `/meters` and sets a session cookie:

```text
__Secure-better-auth.session_token
```

I used the same HTTPX client for login and subsequent requests so the cookie is sent automatically.

## 2. Meter Search

**Endpoint:** `GET /portal/meters/search`

Parameters:
- `q` — Search text
- `page` — Page number

Example:

```http
GET /portal/meters/search?q=J100001&page=1
```

Response structure:

```json
{
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
```

An empty search returned 403 meters, with 20 records per page.

Searching using a lowercase meter ID also worked.

## 3. Meter Details

**Endpoint:**

```http
GET /meters/{meter_id}/__data.json?x-sveltekit-invalidated=001
```

This was the tricky part.

Unlike the search endpoint, the response contains SvelteKit serialized data inside `nodes`.

The meter data was available at:

```python
response["nodes"][2]["data"]
```

Some values are stored as references to other indexes in the same array.

For example:

```json
[
  {"meterId": 1},
  "J100001"
]
```

Here, `1` points to the value at index 1.

I added `decoder.py` to resolve these references recursively and convert the response into normal JSON.

The decoded response contains meter details such as serial number, make, phase type, and installation status.

It also includes the network hierarchy:

```text
Zone → Circle → Division → Subdivision → Substation → Feeder → DT
```

## 4. Meter Location

**Endpoint:** `GET /portal/meters/{meter_id}/geo`

Example response:

```json
{
  "data": {
    "latitude": "26.938961002479868",
    "longitude": "75.83095696146852"
  }
}
```

The coordinates are returned as strings.

For an invalid meter ID, the portal returned HTTP 404.

## 5. Energy Readings

**Endpoint:** `GET /portal/meters/{meter_id}/energy`

Example response:

```json
{
  "data": [
    {
      "timestamp": "23/06/2026 23:30",
      "kwh": "48438.74",
      "kvah": "52313.84",
      "voltR": "226"
    }
  ]
}
```

The timestamps are in `DD/MM/YYYY HH:mm` format.

The readings I inspected were around 30 minutes apart. The measurement values are returned as strings.

An invalid meter ID returned HTTP 404.

## 6. Error Handling and Limitations

The API currently handles upstream HTTP errors and connection failures.

For location and energy, an upstream 404 is returned as 404 by the API. Other upstream failures generally return 502.

For meter details, I added an existence check using the meter search endpoint before requesting the SvelteKit data. This avoids decoding invalid meter responses and returns 404 when the meter is not found.

The implementation also logs in for each API request. Session reuse and better handling of unexpected portal responses would be the next improvements.