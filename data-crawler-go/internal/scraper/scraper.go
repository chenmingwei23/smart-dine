package scraper

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/chromedp/cdproto/cdp"
	"github.com/chromedp/chromedp"
)

// Scraper represents the Google Maps scraper
type Scraper struct {
	ctx    context.Context
	cancel context.CancelFunc
}

// NewScraper creates a new instance of the scraper
func NewScraper() (*Scraper, error) {
	log.Println("Initializing scraper...")

	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
		chromedp.Flag("disable-gpu", true),
		chromedp.Flag("no-sandbox", true),
		chromedp.Flag("disable-dev-shm-usage", true),
		chromedp.Flag("disable-web-security", true),
		chromedp.Flag("disable-extensions", true),
		chromedp.Flag("disable-notifications", true),
		chromedp.Flag("disable-popup-blocking", true),
		chromedp.Flag("log-level", "2"),
		chromedp.Flag("window-size", "1920,1080"),
		chromedp.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
	)

	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)

	// Create a new chrome instance
	ctx, _ := chromedp.NewContext(
		allocCtx,
		chromedp.WithLogf(log.Printf),
		chromedp.WithDebugf(log.Printf),
	)

	// Create a timeout context
	ctx, cancel = context.WithTimeout(ctx, 30*time.Second)

	// Start the browser
	if err := chromedp.Run(ctx); err != nil {
		cancel()
		return nil, fmt.Errorf("failed to start browser: %v", err)
	}

	return &Scraper{
		ctx:    ctx,
		cancel: cancel,
	}, nil
}

// Close closes the scraper and releases resources
func (s *Scraper) Close() {
	if s.cancel != nil {
		s.cancel()
	}
}

// ScrapePlace scrapes details for a single place
func (s *Scraper) ScrapePlace(url string) (*Place, error) {
	log.Printf("Scraping place: %s", url)

	var place Place
	place.Link = url

	// Navigate to the place page
	if err := chromedp.Run(s.ctx, chromedp.Navigate(url)); err != nil {
		return nil, fmt.Errorf("failed to navigate to place: %v", err)
	}

	// Wait for the main content to load
	if err := chromedp.Run(s.ctx, chromedp.WaitVisible(`h1.DUwDvf`, chromedp.ByQuery)); err != nil {
		return nil, fmt.Errorf("failed to wait for content: %v", err)
	}

	// Extract place details
	var placeData string
	err := chromedp.Run(s.ctx, chromedp.Evaluate(`
		(() => {
			const place = {};
			
			// Get name
			const nameElem = document.querySelector('h1.DUwDvf');
			if (nameElem) {
				place.name = nameElem.textContent.trim();
			}

			// Get rating
			const ratingElem = document.querySelector('span.ceNzKf');
			if (ratingElem) {
				const rating = parseFloat(ratingElem.textContent.trim());
				if (!isNaN(rating)) {
					place.rating = rating;
				}
			}

			// Get review count
			const reviewElem = document.querySelector('button[jsaction*="pane.rating.moreReviews"]');
			if (reviewElem) {
				const match = reviewElem.textContent.match(/([0-9,]+)\s+reviews?/);
				if (match) {
					place.review_count = parseInt(match[1].replace(/,/g, ''));
				}
			}

			// Get categories
			const categoryElems = document.querySelectorAll('button[jsaction*="pane.rating.category"]');
			place.categories = Array.from(categoryElems).map(elem => elem.textContent.trim());
			if (place.categories.length > 0) {
				place.category = place.categories[0];
			}

			// Get address
			const addressElem = document.querySelector('button[data-item-id*="address"]');
			if (addressElem) {
				place.address = addressElem.textContent.trim();
			}

			// Get thumbnail
			const imgElem = document.querySelector('button[data-item-id*="photos"] img');
			if (imgElem) {
				place.thumbnail = imgElem.src;
			}

			// Get price level
			const priceElem = document.querySelector('span[aria-label*="Price"]');
			if (priceElem) {
				place.price_range = priceElem.textContent.trim();
			}

			return JSON.stringify(place);
		})()
	`, &placeData))

	if err != nil {
		return nil, fmt.Errorf("failed to extract place data: %v", err)
	}

	if err := json.Unmarshal([]byte(placeData), &place); err != nil {
		return nil, fmt.Errorf("failed to parse place data: %v", err)
	}

	return &place, nil
}

// ScrapeGoogleMaps scrapes Google Maps for places matching the query
func (s *Scraper) ScrapeGoogleMaps(query string) ([]Place, error) {
	log.Printf("Starting Google Maps scraper for query: %s", query)

	// Create output directory if it doesn't exist
	if err := os.MkdirAll("output", 0755); err != nil {
		return nil, fmt.Errorf("failed to create output directory: %v", err)
	}

	// Construct the search URL
	searchURL := fmt.Sprintf("https://www.google.com/maps/search/%s", strings.ReplaceAll(query, " ", "+"))

	// Navigate to the search URL
	if err := chromedp.Run(s.ctx, chromedp.Navigate(searchURL)); err != nil {
		return nil, fmt.Errorf("failed to navigate to search URL: %v", err)
	}

	// Wait for the results to load
	if err := chromedp.Run(s.ctx, chromedp.WaitVisible(`div[role="feed"]`)); err != nil {
		return nil, fmt.Errorf("failed to wait for results: %v", err)
	}

	// Scroll to load more results
	if err := chromedp.Run(s.ctx, chromedp.Evaluate(`
		(() => {
			const feed = document.querySelector('div[role="feed"]');
			if (!feed) return;
			
			let lastHeight = 0;
			const maxScrolls = 10;
			let scrollCount = 0;
			
			const scroll = () => {
				window.scrollTo(0, document.body.scrollHeight);
				const newHeight = document.body.scrollHeight;
				
				if (newHeight > lastHeight && scrollCount < maxScrolls) {
					lastHeight = newHeight;
					scrollCount++;
					setTimeout(scroll, 1000);
				}
			};
			
			scroll();
		})()
	`, nil)); err != nil {
		log.Printf("Warning: failed to scroll: %v", err)
	}

	// Wait for scrolling to complete
	time.Sleep(5 * time.Second)

	// Get all place nodes
	var nodes []*cdp.Node
	if err := chromedp.Run(s.ctx, chromedp.Nodes(`div[role="feed"] > div > div > a[href*="maps/place"]`, &nodes)); err != nil {
		return nil, fmt.Errorf("failed to get place nodes: %v", err)
	}

	log.Printf("Found %d place nodes", len(nodes))

	var places []Place
	for _, node := range nodes {
		place, err := s.extractPlaceFromNode(node)
		if err != nil {
			log.Printf("Error extracting place: %v", err)
			continue
		}
		if place != nil {
			places = append(places, *place)
		}
	}

	log.Printf("Successfully extracted %d places", len(places))

	// Save results to file
	timestamp := time.Now().Format("20060102_150405")
	outputFile := filepath.Join("output", fmt.Sprintf("places_%s.json", timestamp))

	outputData, err := json.MarshalIndent(places, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("failed to marshal places data: %v", err)
	}

	if err := os.WriteFile(outputFile, outputData, 0644); err != nil {
		return nil, fmt.Errorf("failed to write output file: %v", err)
	}

	log.Printf("Successfully saved %d places to %s", len(places), outputFile)
	return places, nil
}

func (s *Scraper) extractPlaceFromNode(node *cdp.Node) (*Place, error) {
	var placeData string
	err := chromedp.Run(s.ctx, chromedp.Evaluate(fmt.Sprintf(`
		(() => {
			const node = document.evaluate('%s', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
			if (!node) return null;

			const place = {};
			
			// Get name and link from the parent a tag
			const linkElem = node.closest('a[href*="maps/place"]');
			if (linkElem) {
				place.link = linkElem.href;
				const cidMatch = place.link.match(/0x[0-9a-fA-F]+:/);
				if (cidMatch) {
					place.cid = cidMatch[0].slice(0, -1);
				}
			} else {
				return null;
			}

			// Get name from heading
			const nameElem = node.querySelector('.fontHeadlineLarge');
			if (nameElem) {
				place.name = nameElem.textContent.trim();
			} else {
				return null;
			}

			// Get rating
			const ratingElem = node.querySelector('span.fontDisplayLarge');
			if (ratingElem) {
				const ratingText = ratingElem.textContent.trim();
				const ratingMatch = ratingText.match(/([0-9]+(\.[0-9]+)?)/);
				if (ratingMatch) {
					place.rating = parseFloat(ratingMatch[1]);
				}
			}

			// Get review count
			const reviewsElem = node.querySelector('span.fontBodyMedium');
			if (reviewsElem) {
				const reviewText = reviewsElem.textContent.trim();
				const reviewMatch = reviewText.match(/([0-9,]+)\s+review/);
				if (reviewMatch) {
					place.review_count = parseInt(reviewMatch[1].replace(/,/g, ''));
				}
			}

			// Get category and address
			const textElems = Array.from(node.querySelectorAll('div.fontBodyMedium'));
			let foundCategory = false;
			textElems.forEach((elem, index) => {
				const text = elem.textContent.trim();
				if (!text) return;
				
				if (!foundCategory && text.includes('·')) {
					const categories = text.split('·').map(cat => cat.trim()).filter(Boolean);
					place.categories = categories;
					if (categories.length > 0) {
						place.category = categories[0];
					}
					foundCategory = true;
				} else if (foundCategory && !place.address) {
					place.address = text;
				}
			});

			// Get thumbnail
			const imgElem = node.querySelector('img[src*="photo"]');
			if (imgElem) {
				place.thumbnail = imgElem.src;
			}

			// Get price level
			const priceElem = node.querySelector('span[aria-label*="Price"]');
			if (priceElem) {
				place.price_range = priceElem.textContent.trim();
			}

			return JSON.stringify(place);
		})()
	`, node.FullXPath()), &placeData))

	if err != nil {
		return nil, fmt.Errorf("failed to evaluate node: %v", err)
	}

	if placeData == "" || placeData == "null" {
		return nil, nil
	}

	var place Place
	if err := json.Unmarshal([]byte(placeData), &place); err != nil {
		return nil, fmt.Errorf("failed to parse place data: %v", err)
	}

	return &place, nil
}
