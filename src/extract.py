import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def extract_coinpost_headlines():
    url = "https://coinpost.jp/"

    # Mimic a real web browser to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    print(f"Fetching data from {url}...")

    # Use response.content for raw bytes to perfectly preserve Japanese characters
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Target ONLY the main news section wrapper to avoid video/old commentary tabs
    # CoinPost places the primary breaking news feed in the first 'hmml-top' block
    main_news_section = soup.find(class_="hmml-top")

    if main_news_section:
        # Find every article container using the discovered class
        articles = main_news_section.find_all(class_="homelist-in")
    else:
        # Fallback if structure changes slightly
        articles = soup.find_all(class_="homelist-in")[:12]

    data_payload = []
    seen_urls = set()  # Used to deduplicate articles across tabs
    current_time = datetime.now().isoformat()

    for article in articles:
        # Find the text container
        title_container = article.find(class_="homelist-in-text")
        if not title_container:
            continue

        # 1. Extract the Link (URL)
        link_element = title_container.find("a")
        link = link_element["href"] if link_element else None

        # Skip if no link or if already scraped this exact article URL
        if not link or link in seen_urls:
            continue

        # 2. Extract Timestamp cleanly from the sub-class
        sub_date_element = title_container.find(class_="homelist-in-sub")
        published_date_raw = sub_date_element.get_text(strip=True) if sub_date_element else None

        # 3. Remove the sub-date element from the tree so it doesn't contaminate the headline
        if sub_date_element:
            sub_date_element.decompose()

        # 4. Extract clean headline
        headline = title_container.get_text(strip=True)

        # Track seen links to avoid duplicates
        seen_urls.add(link)

        data_payload.append({
            "article_id": link,
            "headline_raw": headline,
            "published_date_raw": published_date_raw,
            "scraped_at": current_time
        })

    print(f"Successfully extracted {len(data_payload)} targeted breaking news articles.")
    return data_payload

def save_raw_data(data):
    """Saves the extracted data array into data/raw/ as a JSON file."""
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, "raw_headlines.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved raw payload to: {file_path}")


if __name__ == "__main__":
    # Execute the function and print the very first article to test it
    extracted_data = extract_coinpost_headlines()

    if extracted_data:
        save_raw_data(extracted_data)
