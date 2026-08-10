# Rise of the Underdogs

Responsive Next.js 15 interface with three routes:
- `/` — landing page and interactive map
- `/stories` — blind agentic story / human-written story comparison plus visualizations
- `/evaluation` — five-criterion rating interface

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
