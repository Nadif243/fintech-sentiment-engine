import sys
import time
import argparse
import logging
from datetime import datetime

# Import custom ETL modules from src/
from src.extract import extract_coinpost_headlines, save_raw_data
from src.transform import process_data
from src.load import load_processed_data, verify_database

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run_pipeline():
    """Executes the complete ETL pipeline end-to-end with timing and error handling."""
    start_time = time.time()
    logging.info("=" * 60)
    logging.info("STARTING FINTECH SENTIMENT ETL PIPELINE RUN")
    logging.info("=" * 60)

    try:
        # Phase 1: Ingestion (Extract)
        logging.info("[1/3] Step: Extracting raw headlines from CoinPost...")
        raw_data = extract_coinpost_headlines()
        if not raw_data:
            logging.warning("No data extracted. Aborting pipeline run.")
            return
        save_raw_data(raw_data)

        # Phase 2: Refinement (Transform via Gemini API)
        logging.info("[2/3] Step: Transforming text & performing batch sentiment analysis...")
        process_data()

        # Phase 3: Storage (Load into SQLite)
        logging.info("[3/3] Step: Loading processed payload into SQLite database...")
        load_processed_data()

        # Verification & Execution Summary
        duration = round(time.time() - start_time, 2)
        logging.info(f"ETL PIPELINE RUN COMPLETED SUCCESSFULLY in {duration} seconds.")
        logging.info("=" * 60)

        # Run DB query snapshot
        verify_database()

    except Exception as e:
        logging.error(f"CRITICAL: Pipeline run failed due to error: {e}", exc_info=True)

def start_scheduler(interval_minutes: int):
    """Runs the pipeline in a scheduled loop every N minutes."""
    logging.info(f"Starting pipeline scheduler. Running every {interval_minutes} minutes...")
    logging.info("Press Ctrl+C to stop the process.")

    # Run immediately on startup
    run_pipeline()

    try:
        while True:
            # Wait for the specified interval
            time.sleep(interval_minutes * 60)
            run_pipeline()
    except KeyboardInterrupt:
        logging.info("\nScheduler manually stopped by user. Exiting cleanly.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FinTech Sentiment Engine Pipeline Orchestrator")
    parser.add_argument(
        "--schedule",
        type=int,
        help="Run the pipeline in loop mode every N minutes (e.g., --schedule 60)"
    )

    args = parser.parse_args()

    if args.schedule:
        start_scheduler(args.schedule)
    else:
        run_pipeline()
