# Japanese FinTech Sentiment Engine
**日本のフィンテック・センチメント・エンジン**

An automated ETL data pipeline that extracts Japanese financial news, processes the text using natural language processing (NLP), and outputs sentiment analysis for market research.

## プロジェクトの目的 (Project Purpose)
This project demonstrates modern data engineering principles, handling everything from data ingestion to text tokenization.
* **データ抽出 (Data Extraction):** Scraping live financial news.
* **前処理 (Preprocessing / Transformation):** Tokenizing complex kanji using SudachiPy and scoring sentiment.
* **自動化 (Automation):** Running the pipeline as a scheduled batch job.

## 技術スタック (Tech Stack)
* **言語 (Language):** Python
* **ライブラリ (Libraries):** `requests`, `BeautifulSoup`, `pandas`, `SudachiPy`
* **インフラ (Infrastructure):** Docker, AWS (Planned)

## 使い方 (How to Use)
1. Install dependencies: `pip install -r requirements.txt`
2. Run the extraction script: `python src/extract.py`
