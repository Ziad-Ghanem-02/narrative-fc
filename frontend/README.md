# Rise of the Underdogs

Responsive Next.js 15 interface with these routes:
- `/` — landing page and interactive map
- `/stories` — blind agentic story / human-written story comparison plus visualizations
- `/evaluation` — five-criterion rating interface
- `/reviews` — aggregate ratings, story preferences, and anonymous written reviews
- `/dev-chart-test` — chart renderer development page

## Required map file
Copy your TopoJSON/GeoJSON file to:

`public/world-countries.json`

The map component expects country names in `properties.NAME`, `properties.name`, or `properties.ADMIN`.

## Run
```bash
npm install
npm run dev
```
Then open `http://localhost:3000`.

The frontend expects the Django API proxy target in `BACKEND_API_URL`, defaulting
to `http://127.0.0.1:8000`. See the repository [README](../README.md) for the
full-stack setup and deployment instructions.
