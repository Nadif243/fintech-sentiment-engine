# Japanese FinTech Sentiment Engine
**日本のフィンテック・センチメント・エンジン**

An automated, containerized ETL data pipeline that extracts real-time Japanese financial news, utilizes LLM-based natural language processing for dynamic sentiment analysis, and serves the structured data via a REST API.

## 🎯 Project Overview & Motivation
This project was built as a hands-on learning initiative to transition from academic computational physics to modern backend and data engineering.

Rather than stopping at manual Python scripts, the goal was to build a complete, "set-it-and-forget-it" system to understand how data flows from ingestion to a consumable API. Additionally, scraping real-time Japanese financial news provides organic, high-level vocabulary for my daily language immersion and SRS study routines.

### Dual-Purpose Motivation
This system was built with two primary goals:
1. **Engineering Transition:** Applying the analytical rigor and mathematical problem-solving methodologies developed through computational physics research to modern, scalable backend engineering.
2. **Language Immersion:** Creating an automated pipeline to source high-level native Japanese financial and technical vocabulary, providing organic material for spaced repetition (SRS) study environments.

## 🏗️ System Architecture

```text
[Ingestion]           [Transformation]           [Storage]               [Serving]
CoinPost (Web) ──► extract.py ──► Gemini API ──► load.py (SQLite) ──► api.py (FastAPI) ──► Swagger UI
```

## Core Pipeline
- Extraction: Scrapes live breaking news from crypto media.
- **Transformation:** Uses the Google Gemini API to bypass legacy NLP libraries, dynamically extracting crypto tickers and scoring sentiment.
- **Storage:** Implements idempotent SQL logic (Upserts) in SQLite to handle duplicates safely during automated runs.
- **Serving:** Uses FastAPI to serve the data headlessly, completely decoupled from the data extraction layer.

## 🧠 Lessons Learned & Future Improvements
As a beginner to production-grade architecture, this project introduced several key learning milestones:
- **Orchestration:** Moving from executing sequential scripts in a terminal to building a centralized `main.py` orchestrator.
- **Containerization:** Learning how Docker isolates environments and how Docker Compose links background workers with live web servers.
- **Next Steps:** While the current system is stable locally, my future goals include adding unit tests (`pytest`), migrating from SQLite to PostgreSQL, and deploying to a cloud provider.
* **Pipeline Resiliency (Multi-Source Extraction):** Expanding the extraction layer to aggregate news from multiple Japanese financial outlets (e.g., Cointelegraph Japan, CoinDesk Japan) to eliminate single points of failure (SPOF) in the HTML scrapers and reduce editorial bias in the aggregate sentiment scores.

## 🚀 Quick Start (Docker)
1. **Clone the repository and configure credentials:** Rename `.env.example` to `.env` and add your Google Gemini API key.
```
	GEMINI_API_KEY=your_api_key_here
```

2. **Launch the engine:**
```Bash
    docker compose up -d --build
```

3. **Explore the Data:** Open your browser and navigate to the interactive Swagger UI: 👉 **`http://localhost:8000/docs`**
