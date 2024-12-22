package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"smart-dine/data-crawler-go/internal/scraper"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)
	log.Println("Starting crawler application...")

	// Create a new scraper instance
	s, err := scraper.NewScraper()
	if err != nil {
		log.Fatalf("Failed to create scraper: %v", err)
	}
	defer s.Close()

	// Example search parameters
	query := "restaurants in New York"
	log.Printf("Searching for: %s", query)

	// Run the scraper
	places, err := s.ScrapeGoogleMaps(query)
	if err != nil {
		log.Fatalf("Failed to run scraper: %v", err)
	}

	log.Printf("Found %d places", len(places))

	// Create output directory if it doesn't exist
	outputDir := "output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Save results to a JSON file
	filename := filepath.Join(outputDir, fmt.Sprintf("places_%s.json", time.Now().Format("20060102_150405")))
	file, err := os.Create(filename)
	if err != nil {
		log.Fatalf("Failed to create output file: %v", err)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(places); err != nil {
		log.Fatalf("Failed to encode results: %v", err)
	}

	log.Printf("Successfully scraped %d places. Results saved to %s", len(places), filename)
}
