# Starbridge Signal Radar

A tiny standalone GTM intelligence product built for Starbridge. It detects companies actively investing in U.S. public-sector GTM, ranks the signals, and gives Starbridge a clear outreach angle.

## What the CRO can do

- Open one URL
- Pick a 7-day, 30-day, or 1-year signal window
- Click **Run live scan**
- See ranked companies with the source evidence attached
- Read a concise **Why now** and **Starbridge angle**
- Copy an account brief or export the list to CSV
- Share the same URL with the growth team

No Clay, CRM, or login is required.

## How it works

1. The backend runs six targeted public-web searches for fresh SLED, public-sector, state/local, and higher-ed sales expansion signals.
2. Tavily returns current search results and source URLs.
3. OpenAI classifies only the supplied evidence, dedupes companies, scores intent, and generates a Starbridge-specific reason to engage.
4. The UI ranks the results and preserves the source URL for verification.

The live backend deliberately does **not** scrape LinkedIn or depend on browser automation.

## Run locally

```bash
npm install
cp .env.example .env.local
# add your keys to .env.local
npm run dev
```

Then open http://localhost:3000.

If API keys are missing, the app automatically loads a demo dataset so the interface still works.

## Environment variables

```bash
TAVILY_API_KEY=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-luna
```

## Deploy to Vercel

1. Push this folder to a new GitHub repo.
2. Import the repo into Vercel.
3. Add the three environment variables above in Vercel project settings.
4. Deploy.
5. Send the resulting URL to Starbridge.

## MVP scope on purpose

The app does **not** try to be a full outbound sequencer. It does one useful thing well: tell Starbridge which vendors are showing fresh evidence of public-sector GTM investment and why they may be worth working now.

Good next additions if the team actually uses it:

- daily scheduled scan and email/Slack digest
- saved/dismissed signals
- company watchlist
- CRM lookup to suppress existing opportunities/customers
- automatic contact discovery
- team notes and ownership
- feedback loop on whether a signal converted to a meeting
