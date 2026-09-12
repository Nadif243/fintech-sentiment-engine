import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

# Load API key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY not found in .env file")

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# 1. Define the Batch Data Structure
class ArticleSentiment(BaseModel):
    article_id: str = Field(description="The exact article_id provided in the input.")
    sentiment_score: float = Field(description="A float between -1.0 (bearish) and 1.0 (bullish).")
    assets_mentioned: list[str] = Field(description="List of standard crypto tickers (e.g., 'BTC').")
    reasoning: str = Field(description="1-sentence Japanese explanation of the score.")

class BatchSentimentResponse(BaseModel):
    items: list[ArticleSentiment]

def analyze_japanese_sentiment_batch(articles: list[dict]) -> dict:
    """Sends all articles in a single API request to avoid Rate Limits."""

    # Prepare a minimal payload to send to the LLM to save tokens
    prompt_payload = [{"article_id": a["article_id"], "headline": a["headline_raw"]} for a in articles]

    prompt = f"""
    You are an expert Japanese financial quantitative analyst.
    Analyze this JSON array of crypto news headlines.
    Return a JSON object containing an 'items' array with the exact same article_ids,
    mapping each to its calculated sentiment score, assets, and reasoning.

    Input Data:
    {json.dumps(prompt_payload, ensure_ascii=False)}
    """

    # Using the current 3.6-flash model as required by the platform
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': BatchSentimentResponse,
            'temperature': 0.1 # Low temperature ensures deterministic, analytical outputs
        },
    )

    # The API returns a strict JSON string matching our Pydantic model
    return json.loads(response.text)

def process_data():
    input_path = "data/raw/raw_headlines.json"
    output_dir = "data/processed"
    output_path = os.path.join(output_dir, "processed_headlines.json")

    # Ensure processed directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the raw data
    print(f"Loading raw data from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"Initiating LLM API batch transformation for {len(raw_data)} articles...")

    try:
        # 1 Request. 1 Quota Hit. 100% Efficiency.
        batch_results = analyze_japanese_sentiment_batch(raw_data)

        # Create a lookup dictionary from the LLM response for easy merging
        analysis_lookup = {item["article_id"]: item for item in batch_results.get("items", [])}

        processed_data = []

        # Merge the LLM analysis back with our original scraped timestamps
        for item in raw_data:
            analysis = analysis_lookup.get(item["article_id"])
            if analysis:
                processed_item = {
                    "article_id": item["article_id"],
                    "published_date_raw": item["published_date_raw"],
                    "headline_raw": item["headline_raw"],
                    "sentiment_score": analysis["sentiment_score"],
                    "assets_mentioned": analysis["assets_mentioned"],
                    "reasoning": analysis["reasoning"],
                    "processed_at": item["scraped_at"]
                }
                processed_data.append(processed_item)
            else:
                print(f"Warning: LLM missed article {item['article_id']}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        print(f"\nSuccessfully processed {len(processed_data)} articles in a single batch.")
        print(f"Saved processed payload to: {output_path}")

    except Exception as e:
        print(f"Batch Processing Error: {e}")

if __name__ == "__main__":
    process_data()
