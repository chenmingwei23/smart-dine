package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"smart-dine/data-crawler-go/internal/crawler"
)

func main() {
	// Parse command line flags
	var (
		query = flag.String("query", "restaurants", "Search term")
		lat   = flag.Float64("lat", -33.899109, "Latitude")
		lon   = flag.Float64("lng", 151.209469, "Longitude")
		out   = flag.String("out", "output", "Output directory")
	)
	flag.Parse()

	// Create output directory
	if err := os.MkdirAll(*out, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Initialize scraper
	scraper := crawler.NewScraper()
	defer scraper.Close()

	// Start scraping
	log.Printf("Starting scraper for %s around (%f, %f)", *query, *lat, *lon)
	places, err := scraper.Run(*query, *lat, *lon)
	if err != nil {
		log.Fatalf("Scraping failed: %v", err)
	}

	// Save results
	timestamp := time.Now().Format("20060102_150405")
	filename := filepath.Join(*out, fmt.Sprintf("places_%s_%s.json", *query, timestamp))
	
	file, err := os.Create(filename)
	if err != nil {
		log.Fatalf("Failed to create output file: %v", err)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(places); err != nil {
		log.Fatalf("Failed to write results: %v", err)
	}

	log.Printf("Successfully scraped %d places. Results saved to %s", len(places), filename)
}
