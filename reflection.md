# Reflection

## Approach

I started by exploring the Urja Meter Ops portal and checking the network requests in Chrome DevTools.

My main goal was to understand how the portal handles authentication and retrieves meter information. Once I identified the required endpoints, I implemented a FastAPI service using HTTPX to make those requests.

I kept the portal communication logic separate from the API routes to make the code easier to understand and maintain.

## Assumptions

I assumed the portal endpoints would continue working in the same way as they did during my investigation. Since the task was to provide read-only access, I focused only on retrieving data.

I also assumed that keeping the original energy values and timestamps was acceptable for the initial API, instead of converting them into different formats.

## Challenges

The most challenging part was handling the meter details response.

The search, location, and energy endpoints returned normal JSON, but the meter details endpoint returned SvelteKit serialized data with indexed references.

I had to understand how those references worked and write a decoder to convert the response into a usable JSON structure.

Another challenge was handling authentication correctly, especially maintaining the session cookie between login and subsequent requests.

## Mistake I Made

Initially, I directly called the meter details endpoint without checking whether the meter ID existed.

When I tested an invalid meter ID, the API returned 502 instead of 404 because the SvelteKit response could not be decoded properly.

I fixed this by checking the meter ID through the search endpoint before fetching its details. This also helped me improve the error handling.

## What I Would Improve

Given more time, I would focus on:

- Reusing authenticated sessions instead of logging in for every request.
- Adding more detailed error handling for unexpected portal responses.
- Adding Pydantic response models for better API documentation.
- Adding more integration tests.

I kept the implementation simple and focused on the main requirements.

## Self-Review

If I were reviewing this project, I would point out that the API logs in for every request, which adds unnecessary overhead.

Another limitation is that the decoder depends on the portal's current SvelteKit response structure. If the portal changes that format, the decoder may need updates.

I would also improve the response schemas and add more tests for unexpected portal responses.

## AI Assistance

I used AI tools for guidance while understanding the SvelteKit response format, debugging errors, reviewing code, and preparing documentation.

I also used AI assistance while developing the API and tests. I checked the suggestions against the portal responses and tested the implementation locally.

The portal investigation and verification were carried out using Chrome DevTools and local testing.