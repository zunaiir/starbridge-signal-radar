# Starbridge Signal Radar — Flat Upload Version

This version is intentionally **folder-free** so every project file can be uploaded directly into the root of a GitHub repository from the browser.

## Files to upload

Upload all of these at the repository root:

- `main.py`
- `requirements.txt`
- `vercel.json`
- `.env.example` (optional; do not put real keys in this file)

You do not need `app/`, `api/`, `package.json`, or any other folders.

## Deploy on Vercel

1. Import the GitHub repository into Vercel.
2. Add these environment variables in Vercel Project Settings:
   - `TAVILY_API_KEY`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` = `gpt-5.6-luna`
3. Deploy.
4. Open the generated `.vercel.app` URL.
5. Click **Run live scan**. The Mode value should switch to `live` when both API keys are working.

## How it works

`main.py` contains both the frontend and the backend. The browser calls `/scan`; the Flask backend searches Tavily and sends the search evidence to the OpenAI Responses API for scoring and summarization.

The API keys stay server-side and are never embedded in the page.
