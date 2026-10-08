# Graph knowledge console

React + TypeScript frontend for the Agentic Knowledge Graph API.

## Development

The FastAPI service must be running on `http://127.0.0.1:8000`.

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Checks

```powershell
npm run lint
npm run build
```

The browser only talks to FastAPI. Groq, Tavily, Neo4j, and model credentials remain on the backend and are never exposed through Vite.
