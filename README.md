# Tokyo Land Price RAG

<img width="3024" height="1964" alt="screenshot" src="https://github.com/user-attachments/assets/3ae0c6b7-8a9b-4abd-acd1-ad39f02bbc24" />

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Retrieval-Augmented Generation (RAG) application for exploring Tokyo land prices using an interactive map

## Setup

### Prerequisites

- [Mapbox API key](https://www.mapbox.com)
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Docker](https://www.docker.com)
- [uv](https://docs.astral.sh/uv/)

1. Create the environment files:

```bash
cp .env.example .env
cp client/.env.example client/.env
```

Set `OPENAI_API_KEY` in `.env` and `VITE_MAPBOX_TOKEN` in `client/.env`.

2. Start the services:

```bash
docker compose up -d
```

3. Initialize Qdrant:

```bash
cd scripts && uv run python init_qdrant.py
```

This replaces the existing collection and generates embeddings using the OpenAI
API, which may incur charges.

4. Access http://localhost:5173/.

### Example questions

- Which areas in Tokyo have the highest land prices?
- Where are good residential areas near Shibuya?

## Tech Stack

- Frontend: Vue
- Backend: Django
- LLM: OpenAI API
- Vector Search DB: Qdrant
- Local Development: Docker
- Others: OpenStreetMap, Mapbox, Maplibre

## Contribution

- Bug fix PRs are always appreciated.
- UI changes or new features should not be submitted without prior discussion. Please open an issue first to propose and discuss them.

Thanks for your understanding and contributions.

## Credits

- 国土数値情報 （地価公示データ）(Ministry of Land, Infrastructure, Transport and Tourism) https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2025.html
- 国土数値情報 （行政地区データ）(Ministry of Land, Infrastructure, Transport and Tourism) https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html

  The original data has been processed and transformed for visualization purposes.

## License

[MIT](./LICENSE)

Copyright (c) 2026-present, Akinori Hoshina
