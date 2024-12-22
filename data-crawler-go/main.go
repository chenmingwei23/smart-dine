package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"regexp"
	"time"

	"github.com/chromedp/cdproto/cdp"
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

func scrapePlaces(ctx context.Context) error {
	// Navigate directly to the search results
	log.Printf("Step 1: Navigating to Google Maps search page...")
	searchURL := "https://www.google.com/maps/search/restaurants+in+New+York"
	if err := chromedp.Run(ctx,
		chromedp.Navigate(searchURL),
		chromedp.Sleep(5*time.Second),
	); err != nil {
		return fmt.Errorf("failed to navigate: %v", err)
	}

	log.Printf("Step 2: Waiting for main content to load...")
	if err := chromedp.Run(ctx,
		// Wait for the main content area
		chromedp.WaitVisible(`div[role="main"]`, chromedp.ByQuery),
		chromedp.Sleep(2*time.Second),
	); err != nil {
		return fmt.Errorf("failed to wait for main content: %v", err)
	}

	// Wait for and check the search box state
	log.Printf("Step 3: Checking search box state...")
	var searchBoxVisible bool
	if err := chromedp.Run(ctx,
		chromedp.Evaluate(`!!document.querySelector('input#searchboxinput')`, &searchBoxVisible),
	); err != nil {
		log.Printf("Warning: Could not check search box: %v", err)
	}
	log.Printf("Search box visible: %v", searchBoxVisible)

	// Wait for the results container
	log.Printf("Step 4: Waiting for results container...")
	if err := chromedp.Run(ctx,
		chromedp.WaitVisible(`div[role="feed"]`, chromedp.ByQuery),
		chromedp.Sleep(3*time.Second),
	); err != nil {
		return fmt.Errorf("failed to wait for results container: %v", err)
	}

	// First, let's check what we can find in the feed
	var feedHTML string
	if err := chromedp.Run(ctx,
		chromedp.OuterHTML(`div[role="feed"]`, &feedHTML, chromedp.ByQuery),
	); err != nil {
		log.Printf("Warning: Could not get feed HTML: %v", err)
	} else {
		log.Printf("\n=== Feed Structure ===\nLength: %d\nFirst 500 chars:\n%s\n===\n",
			len(feedHTML), feedHTML[:min(500, len(feedHTML))])
	}

	// Get all restaurant nodes
	log.Printf("Step 5: Finding restaurant nodes...")
	var nodes []*cdp.Node
	if err := chromedp.Run(ctx,
		// Target the actual restaurant cards
		chromedp.Nodes(`div[role="feed"] > div.Nv2PK`, &nodes, chromedp.ByQueryAll),
	); err != nil {
		return fmt.Errorf("failed to find restaurant nodes: %v", err)
	}

	log.Printf("Found %d restaurant nodes", len(nodes))

	// Get the first non-empty node
	var firstNode *cdp.Node
	for i, node := range nodes {
		log.Printf("Node %d: Type=%s, Name=%s, ChildCount=%d, AttributeCount=%d",
			i+1, node.NodeType, node.NodeName, node.ChildNodeCount, len(node.Attributes))
		if node.ChildNodeCount > 0 {
			firstNode = node
			// Print node attributes
			for i := 0; i < len(node.Attributes); i += 2 {
				log.Printf("  Attribute: %s=%s", node.Attributes[i], node.Attributes[i+1])
			}
			break
		}
	}

	if firstNode == nil {
		// Take a screenshot to help debug
		var buf []byte
		if err := chromedp.Run(ctx,
			chromedp.Screenshot(`div[role="feed"]`, &buf, chromedp.NodeVisible),
		); err != nil {
			log.Printf("Warning: Could not take screenshot: %v", err)
		} else {
			if err := os.WriteFile("debug_screenshot.png", buf, 0644); err != nil {
				log.Printf("Warning: Could not save screenshot: %v", err)
			}
		}
		return fmt.Errorf("no valid restaurant nodes found")
	}

	// Print the entire subtree of the first restaurant
	var html string
	if err := chromedp.Run(ctx,
		chromedp.OuterHTML(firstNode.FullXPath(), &html),
	); err != nil {
		return fmt.Errorf("failed to get HTML: %v", err)
	}

	log.Printf("\n=== First Restaurant Node Structure ===\nLength: %d\nXPath: %s\nContent:\n%s\n===\n",
		len(html), firstNode.FullXPath(), html)

	// Try to find specific elements within this node using JavaScript evaluation
	var result map[string]interface{}
	script := `
		(() => {
			const node = document.evaluate('` + firstNode.FullXPath() + `', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
			if (!node) {
				console.log('Node not found at XPath:', '` + firstNode.FullXPath() + `');
				return { error: 'Node not found' };
			}
			console.log('Found node:', node.outerHTML);
			
			// Helper function to safely get text content
			const getText = (selector) => {
				const elements = node.querySelectorAll(selector);
				console.log('Searching for selector:', selector);
				console.log('Found elements:', Array.from(elements).map(el => el.outerHTML));
				const texts = Array.from(elements).map(el => el.textContent.trim()).filter(t => t);
				console.log('Extracted texts:', texts);
				return texts.join(' ');
			};

			// Helper function to safely get attribute
			const getAttr = (selector, attr) => {
				const elements = node.querySelectorAll(selector);
				console.log('Searching for selector:', selector, 'attribute:', attr);
				console.log('Found elements:', Array.from(elements).map(el => el.outerHTML));
				const attrs = Array.from(elements).map(el => el.getAttribute(attr)).filter(a => a);
				console.log('Extracted attributes:', attrs);
				return attrs[0] || '';
			};

			// Updated selectors for restaurant data
			const nameSelectors = ['div.qBF1Pd', 'div.fontHeadlineSmall', 'div[role="heading"]'];
			const ratingSelectors = ['span.MW4etd', 'span.fontDisplayLarge'];
			const reviewSelectors = ['span.UY7F9', 'span[aria-label*="review"]'];
			const categorySelectors = ['div.W4Efsd:first-child', 'div.fontBodyMedium:first-child'];
			const addressSelectors = ['div.W4Efsd:nth-child(2)', 'div.fontBodyMedium:nth-child(2)'];
			const linkSelectors = ['a[href*="maps/place"]', 'a[jsaction*="placeCard"]'];
			const thumbnailSelectors = ['img[src*="photo"]', 'img[decoding="async"]'];

			const result = {
				name: nameSelectors.map(s => getText(s)).filter(t => t)[0] || '',
				rating: ratingSelectors.map(s => getText(s)).filter(t => t)[0] || '',
				reviews: reviewSelectors.map(s => getText(s)).filter(t => t)[0] || '',
				category: categorySelectors.map(s => getText(s)).filter(t => t)[0] || '',
				address: addressSelectors.map(s => getText(s)).filter(t => t)[0] || '',
				link: linkSelectors.map(s => getAttr(s, 'href')).filter(t => t)[0] || '',
				thumbnail: thumbnailSelectors.map(s => getAttr(s, 'src')).filter(t => t)[0] || '',
				debug: {
					classes: Array.from(node.querySelectorAll('*')).map(el => ({
						tag: el.tagName,
						class: el.className,
						text: el.textContent.trim(),
						html: el.outerHTML
					}))
				}
			};
			console.log('Final result:', result);
			return result;
		})()
	`

	if err := chromedp.Run(ctx, chromedp.Evaluate(script, &result)); err != nil {
		log.Printf("Warning: Failed to extract data: %v", err)
	}

	log.Printf("\n=== Extracted Data ===")
	if result == nil {
		log.Printf("No data extracted (result is nil)")
		return fmt.Errorf("no data extracted")
	}

	log.Printf("Name: %v", result["name"])
	log.Printf("Rating: %v", result["rating"])
	log.Printf("Reviews: %v", result["reviews"])
	log.Printf("Category: %v", result["category"])
	log.Printf("Address: %v", result["address"])
	log.Printf("Link: %v", result["link"])
	log.Printf("Thumbnail: %v", result["thumbnail"])

	if debug, ok := result["debug"].(map[string]interface{}); ok {
		log.Printf("\n=== Debug Info ===")
		if classes, ok := debug["classes"].([]interface{}); ok {
			for _, c := range classes {
				if class, ok := c.(map[string]interface{}); ok {
					log.Printf("\nElement:")
					log.Printf("Tag: %v", class["tag"])
					log.Printf("Class: %v", class["class"])
					log.Printf("Text: %v", class["text"])
				}
			}
		}
	}

	return nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	// Create a new Chrome instance
	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", false), // Run in non-headless mode to see what's happening
		chromedp.Flag("disable-gpu", true),
		chromedp.Flag("no-sandbox", true),
		chromedp.Flag("disable-dev-shm-usage", true),
		chromedp.Flag("start-maximized", true),      // Start with maximized window
		chromedp.Flag("disable-web-security", true), // Disable CORS
		chromedp.Flag("disable-background-networking", false),
		chromedp.Flag("enable-logging", true),
		chromedp.Flag("v", "1"), // Verbose logging
	)

	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()

	// Create a new context with logging
	ctx, cancel := chromedp.NewContext(
		allocCtx,
		chromedp.WithLogf(log.Printf),
		chromedp.WithDebugf(log.Printf),
	)
	defer cancel()

	// Set a timeout for the entire operation (5 minutes)
	ctx, cancel = context.WithTimeout(ctx, 5*time.Minute)
	defer cancel()

	// Create output directory if it doesn't exist
	if err := os.MkdirAll("output", 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Run the scraper
	log.Printf("Starting scraper...")
	if err := scrapePlaces(ctx); err != nil {
		log.Fatalf("Failed to scrape places: %v", err)
	}
	log.Printf("Scraping completed successfully")
}
