from src.simple_crawler import SimpleGoogleMapsCrawler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        crawler = SimpleGoogleMapsCrawler()
        results = crawler.run_test_crawl()
        logging.info(f"Crawling completed. Found {len(results)} places.")
    except Exception as e:
        logging.error(f"Crawling failed: {str(e)}")

if __name__ == "__main__":
    main() 