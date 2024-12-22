package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/chromedp/cdp"
	"github.com/chromedp/chromedp"
)

var (
	cidRegex    = regexp.MustCompile(`0x[0-9a-fA-F]+:`)
	ratingRegex = regexp.MustCompile(`([0-9]+(\.[0-9]+)?)`)
	reviewRegex = regexp.MustCompile(`([0-9,]+)\s+review`)
)

type Place struct {
	Name        string   `json:"name"`
	Link        string   `json:"link"`
	CID         string   `json:"cid"`
	Rating      float64  `json:"rating"`
	ReviewCount int      `json:"review_count"`
	Category    string   `json:"category"`
	Categories  []string `json:"categories"`
	Address     string   `json:"address"`
	Thumbnail   string   `json:"thumbnail"`
	PriceRange  string   `json:"price_range"`
}

func extractPlaceFromNode(node *cdp.Node) (*Place, error) {
	place := &Place{}

	// Get name and link from the parent a tag
	linkElem := node.Parent
	if linkElem == nil || linkElem.NodeName != "a" {
		return nil, fmt.Errorf("failed to find parent link element")
	}

	place.Link = linkElem.AttributeValue("href")
	if cidMatch := cidRegex.FindString(place.Link); cidMatch != "" {
		place.CID = cidMatch[:len(cidMatch)-1]
	}

	// Get name
	nameElem := node.QuerySelector("div.fontHeadlineLarge")
	if nameElem != nil {
		place.Name = strings.TrimSpace(nameElem.TextContent())
	}

	// Get rating
	ratingElem := node.QuerySelector("span.fontDisplayLarge")
	if ratingElem != nil {
		ratingText := strings.TrimSpace(ratingElem.TextContent())
		if ratingMatch := ratingRegex.FindStringSubmatch(ratingText); len(ratingMatch) > 1 {
			if rating, err := strconv.ParseFloat(ratingMatch[1], 64); err == nil {
				place.Rating = rating
			}
		}
	}

	// Get review count
	reviewsElem := node.QuerySelector("span.fontBodyMedium")
	if reviewsElem != nil {
		reviewText := strings.TrimSpace(reviewsElem.TextContent())
		if reviewMatch := reviewRegex.FindStringSubmatch(reviewText); len(reviewMatch) > 1 {
			reviewCount := strings.ReplaceAll(reviewMatch[1], ",", "")
			if count, err := strconv.Atoi(reviewCount); err == nil {
				place.ReviewCount = count
			}
		}
	}

	// Get category and address
	textElems := node.QuerySelectorAll("div.fontBodyMedium")
	foundCategory := false
	for _, elem := range textElems {
		text := strings.TrimSpace(elem.TextContent())
		if text == "" {
			continue
		}

		if !foundCategory && strings.Contains(text, "·") {
			categories := strings.Split(text, "·")
			place.Categories = make([]string, 0)
			for _, cat := range categories {
				cat = strings.TrimSpace(cat)
				if cat != "" {
					place.Categories = append(place.Categories, cat)
				}
			}
			if len(place.Categories) > 0 {
				place.Category = place.Categories[0]
			}
			foundCategory = true
		} else if foundCategory && place.Address == "" {
			place.Address = text
		}
	}

	// Get thumbnail
	imgElem := node.QuerySelector("img[src*=\"photo\"]")
	if imgElem != nil {
		place.Thumbnail = imgElem.AttributeValue("src")
	}

	// Get price level
	priceElem := node.QuerySelector("span[aria-label*=\"Price\"]")
	if priceElem != nil {
		place.PriceRange = strings.TrimSpace(priceElem.TextContent())
	}

	return place, nil
}

func scrapePlaces(ctx context.Context) error {
	// Navigate to Google Maps
	log.Printf("Navigating to Google Maps search page...")
	if err := chromedp.Run(ctx, chromedp.Navigate("https://www.google.com/maps/search/restaurants+in+New+York")); err != nil {
		return fmt.Errorf("failed to navigate: %v", err)
	}

	// Wait for the results to load
	log.Printf("Waiting for results to load...")
	if err := chromedp.Run(ctx, chromedp.WaitVisible(`div[role="feed"]`, chromedp.ByQuery)); err != nil {
		return fmt.Errorf("failed to wait for results: %v", err)
	}

	// Find all place nodes
	var nodes []*cdp.Node
	log.Printf("Finding place nodes...")
	if err := chromedp.Run(ctx, chromedp.Nodes(`div[role="feed"] > div > div > div.Nv2PK`, &nodes, chromedp.ByQueryAll)); err != nil {
		return fmt.Errorf("failed to find place nodes: %v", err)
	}

	log.Printf("Found %d place nodes", len(nodes))

	// Extract information from each place node
	places := make([]*Place, 0)
	for _, node := range nodes {
		place, err := extractPlaceFromNode(node)
		if err != nil {
			log.Printf("Error extracting place: %v", err)
			continue
		}
		places = append(places, place)
	}

	log.Printf("Successfully extracted %d places", len(places))

	// Save results to file
	outputDir := "output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %v", err)
	}

	outputFile := filepath.Join(outputDir, fmt.Sprintf("places_%s.json", time.Now().Format("20060102_150405")))
	jsonData, err := json.MarshalIndent(places, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal places: %v", err)
	}

	if err := os.WriteFile(outputFile, jsonData, 0644); err != nil {
		return fmt.Errorf("failed to write output file: %v", err)
	}

	log.Printf("Successfully saved %d places to %s\n", len(places), outputFile)
	return nil
}

func main() {
	// Create a new Chrome instance
	ctx, cancel := chromedp.NewContext(
		context.Background(),
		chromedp.WithLogf(log.Printf),
	)
	defer cancel()

	// Set a timeout for the entire operation
	ctx, cancel = context.WithTimeout(ctx, 2*time.Minute)
	defer cancel()

	// Run the scraper
	log.Printf("Starting scraper...")
	if err := scrapePlaces(ctx); err != nil {
		log.Fatalf("Failed to scrape places: %v", err)
	}
	log.Printf("Scraping completed successfully")
}
