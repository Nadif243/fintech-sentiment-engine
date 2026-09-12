import os
import json
import sqlite3

DB_PATH = "data/fintech_sentiment.db"
JSON_PATH = "data/processed/processed_headlines.json"

def init_db(conn):
    """Creates the database schema if it doesn't already exist."""
    cursor = conn.cursor()

    # 1. Primary Articles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY,
            headline_raw TEXT NOT NULL,
            published_date_raw TEXT,
            sentiment_score REAL NOT NULL,
            reasoning TEXT,
            processed_at TEXT NOT NULL
        );
    """)

    # 2. Relational Assets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT NOT NULL,
            asset_ticker TEXT NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles (article_id) ON DELETE CASCADE,
            UNIQUE(article_id, asset_ticker)
        );
    """)

    conn.commit()
    print("Database schema initialized successfully.")

def load_processed_data():
    """Reads processed JSON payload and idempotently upserts it into SQLite."""
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"Processed data file not found at {JSON_PATH}. Run transform.py first.")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        articles_data = json.load(f)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Ensure foreign key constraints are enforced in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")

    init_db(conn)
    cursor = conn.cursor()

    inserted_articles = 0
    inserted_assets = 0

    for item in articles_data:
        # 1. Idempotent Upsert into 'articles' table
        cursor.execute("""
            INSERT INTO articles (
                article_id, headline_raw, published_date_raw, sentiment_score, reasoning, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(article_id) DO UPDATE SET
                sentiment_score = excluded.sentiment_score,
                reasoning = excluded.reasoning,
                processed_at = excluded.processed_at;
        """, (
            item["article_id"],
            item["headline_raw"],
            item["published_date_raw"],
            item["sentiment_score"],
            item["reasoning"],
            item["processed_at"]
        ))
        inserted_articles += 1

        # 2. Insert detected assets into 'article_assets' table
        for asset in item.get("assets_mentioned", []):
            cursor.execute("""
                INSERT OR IGNORE INTO article_assets (article_id, asset_ticker)
                VALUES (?, ?);
            """, (item["article_id"], asset))
            if cursor.rowcount > 0:
                inserted_assets += 1

    conn.commit()
    conn.close()

    print(f"Successfully loaded {inserted_articles} articles and {inserted_assets} asset links into {DB_PATH}.")

def verify_database():
    """Runs a quick SQL verification query to demonstrate data retrieval."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n--- DATABASE VERIFICATION (Sample SQL Query) ---")

    # SQL JOIN Query: Find all articles with detected asset tickers
    cursor.execute("""
        SELECT a.published_date_raw, b.asset_ticker, a.sentiment_score, a.headline_raw
        FROM articles a
        JOIN article_assets b ON a.article_id = b.article_id
        ORDER BY a.published_date_raw DESC
        LIMIT 5;
    """)

    rows = cursor.fetchall()
    if rows:
        print(f"{'DATE':<12} | {'ASSET':<6} | {'SCORE':<5} | HEADLINE")
        print("-" * 80)
        for date, asset, score, headline in rows:
            print(f"{date:<12} | {asset:<6} | {score:<5.1f} | {headline[:40]}...")
    else:
        print("No articles with explicit asset tags found yet.")

    conn.close()

if __name__ == "__main__":
    load_processed_data()
    verify_database()
