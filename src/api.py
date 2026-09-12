import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

DB_PATH = "data/fintech_sentiment.db"

app = FastAPI(
    title="Japanese FinTech Sentiment API",
    description="A modern REST API serving real-time Japanese crypto news sentiment and NLP analytics.",
    version="1.0.0"
)

def get_db_connection():
    """Helper to establish a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file not found. Run main.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    return conn

# --- Pydantic API Response Schemas ---

class ArticleResponse(BaseModel):
    article_id: str
    headline_raw: str
    published_date_raw: str
    sentiment_score: float
    reasoning: str
    processed_at: str
    assets: List[str]

class SentimentSummaryResponse(BaseModel):
    asset: str
    total_articles: int
    average_sentiment: float
    market_signal: str

# --- API Endpoints ---

@app.get("/", tags=["Health"])
def root():
    """Root endpoint verifying API health."""
    return {"status": "online", "system": "Japanese FinTech Sentiment Engine API"}

@app.get("/api/v1/headlines", response_model=List[ArticleResponse], tags=["Headlines"])
def get_headlines(limit: int = Query(10, ge=1, le=50)):
    """Fetches the latest processed news articles alongside their sentiment scores and detected assets."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query articles ordered by publication date
    cursor.execute("""
        SELECT article_id, headline_raw, published_date_raw, sentiment_score, reasoning, processed_at
        FROM articles
        ORDER BY processed_at DESC
        LIMIT ?;
    """, (limit,))

    articles = cursor.fetchall()
    result = []

    for row in articles:
        # Fetch associated assets for each article
        cursor.execute("""
            SELECT asset_ticker FROM article_assets WHERE article_id = ?;
        """, (row["article_id"],))
        assets = [asset_row["asset_ticker"] for asset_row in cursor.fetchall()]

        result.append(ArticleResponse(
            article_id=row["article_id"],
            headline_raw=row["headline_raw"],
            published_date_raw=row["published_date_raw"],
            sentiment_score=row["sentiment_score"],
            reasoning=row["reasoning"],
            processed_at=row["processed_at"],
            assets=assets
        ))

    conn.close()
    return result

@app.get("/api/v1/sentiment/{asset_ticker}", response_model=SentimentSummaryResponse, tags=["Analytics"])
def get_asset_sentiment(asset_ticker: str):
    """Calculates the average sentiment score and market signal for a specific crypto asset (e.g., BTC, ETH, XRP)."""
    ticker_upper = asset_ticker.upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.sentiment_score
        FROM articles a
        JOIN article_assets b ON a.article_id = b.article_id
        WHERE b.asset_ticker = ?;
    """, (ticker_upper,))

    scores = [row["sentiment_score"] for row in cursor.fetchall()]
    conn.close()

    if not scores:
        raise HTTPException(status_code=404, detail=f"No sentiment data found for asset ticker: {ticker_upper}")

    avg_score = round(sum(scores) / len(scores), 2)

    # Simple market signal classification
    if avg_score >= 0.3:
        signal = "BULLISH"
    elif avg_score <= -0.3:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    return SentimentSummaryResponse(
        asset=ticker_upper,
        total_articles=len(scores),
        average_sentiment=avg_score,
        market_signal=signal
    )
