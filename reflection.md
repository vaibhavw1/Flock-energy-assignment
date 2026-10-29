# Reflection

## Approach

I started by exploring the Urja Meter Ops portal and checking the network requests in Chrome DevTools.

My main goal was to understand how the portal handles authentication and retrieves meter information. Once I identified the required endpoints, I implemented a FastAPI service using HTTPX to make those requests.

I kept the portal communication logic separate from the API routes to make the code easier to understand and maintain.

## Challenges

The most challenging part was handling the meter details response.

The search, location, and energy endpoints returned normal JSON, but the meter details endpoint returned SvelteKit serialized data with indexed references.

I had to understand how those references worked and write a decoder to convert the response into a usable JSON structure.

Another challenge was handling authentication correctly, especially maintaining the session cookie between login and subsequent requests.

## What I Would Improve

Given more time, I would focus on:

- Reusing authenticated sessions instead of logging in for every request.
- Adding more detailed error handling for unexpected portal responses.
- Adding Pydantic response models for better API documentation.
- Adding more integration tests.

I kept the implementation simple and focused on the main requirements.

## AI Assistance

I used AI tools for guidance while understanding the SvelteKit response format, debugging errors, reviewing code, and preparing documentation.

I also used AI assistance while developing the API and tests. I checked the suggestions against the portal responses and tested the implementation locally.

The portal investigation and verification were carried out using Chrome DevTools and local testing.