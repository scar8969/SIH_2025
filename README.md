# SIH 2025 — Buoy Data SQL Agent

> Ask questions about Indian Ocean moored-buoy data in plain English. A LangGraph agent turns your question into validated SQL, runs it against a 4-year INCOIS ocean dataset, and answers with charts.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-agent-orange)](https://www.langchain.com/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Built for **Smart India Hackathon 2025** — an AI agent that makes oceanographic data from India's moored buoy network (INCOIS) queryable by anyone, no SQL required.

---

## What it does

The system scrapes **4 years of moored-buoy observations** (air/water temperature, wind speed, humidity, rainfall, radiation, pressure) across multiple buoy stations (AD06, AD08, AD10, BD10–BD14), loads them into SQLite, and exposes a natural-language interface:

```
You:  "What was the average wind speed at BD11 in June 2023?"
Agent: SELECT AVG(wind_speed) FROM ... WHERE buoy='BD11' AND month=6 AND year=2023
       → 8.4 m/s 📈 (with a chart)
```

## Architecture

```
┌─────────────┐   ┌──────────────────┐   ┌──────────────┐   ┌─────────────┐
│  Streamlit  │──▶│  LangGraph agent │──▶│  SQL (SQLite)│──▶│  INCOIS DB  │
│   / CLI     │   │  (validated SQL) │   │   execution  │   │  (4-yr data)│
└─────────────┘   └──────────────────┘   └──────────────┘   └─────────────┘
                       │  ▲
                       ▼  │  memory / chat history
                   ┌──────────────┐
                   │  LLM manager │  (OpenAI / OpenRouter)
                   └──────────────┘
```

- **`get_buoy_data.py`** — scraper for INCOIS moored-buoy stock data (per-parameter URLs, configurable year range)
- **`run_master_scraper.py`** — fetches the full buoy metadata list from the INCOIS API and orchestrates bulk scraping
- **`db_toCSV.py`** — exports the SQLite database to CSV
- **`agent/`** — LangGraph workflow: `SQLAgent` (generate + validate SQL) → execute → `DataFormatter` (chart-ready output) → final answer
- **`app.py`** — Streamlit chat UI with conversation memory

## Quick start

```bash
pip install -r requirements.txt   # or: pip install streamlit langgraph langchain-openai pandas

# 1. Set your LLM keys
cp .env.example .env              # fill in OPENAI_API_KEY or OPENROUTER_API_KEY

# 2. (Re)build the database from scraped data
python db_toCSV.py

# 3a. CLI
python main.py

# 3b. Streamlit dashboard
streamlit run app.py
```

## Data

- Source: [INCOIS moored buoy data](https://incois.gov.in/) (Indian National Centre for Ocean Information Services)
- 4-year dataset (`SIH_4yr/`), imported into `data/sih_4y4.db`
- Buoys: AD06, AD08, AD10, BD10, BD11, BD12, BD13, BD14
- Parameters: air & water temperature (multiple depths), air pressure, humidity, wind speed, rainfall, solar radiation

## Security

API keys live in `.env` (git-ignored). `.env.example` documents the required variables.

## License

MIT
