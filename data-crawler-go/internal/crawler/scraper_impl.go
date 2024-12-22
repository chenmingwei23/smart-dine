package crawler

import (
	"context"
	"crypto/md5"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/chromedp/cdproto/cdp"
	"github.com/chromedp/chromedp"
)

func (s *SearchJob) scrollResults() chromedp.Action {
	return chromedp.Evaluate(`
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
	`, nil)
}

func (s *SearchJob) extractPlaceFromNode(ctx context.Context, node *cdp.Node) (*Place, error) {
	var place Place

	var result string
	err := chromedp.Run(ctx,
		chromedp.Evaluate(fmt.Sprintf(`
			(() => {
				const node = document.evaluate('%s', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
				if (!node) {
					console.log('Node not found');
					return null;
				}
				console.log('Found node:', node.outerHTML);

				const place = {};
				
				// Get name and link from the parent a tag
				const linkElem = node.closest('a[href*="maps/place"]');
				if (linkElem) {
					place.link = linkElem.href;
					console.log('Found link:', place.link);
					const cidMatch = place.link.match(/0x[0-9a-fA-F]+:/);
					if (cidMatch) {
						place.cid = cidMatch[0].slice(0, -1);
						console.log('Found CID:', place.cid);
					}
				} else {
					console.log('No link element found');
					return null;
				}

				// Get name from heading
				const nameElem = node.querySelector('div[role="heading"], div.fontHeadlineSmall');
				if (nameElem) {
					place.name = nameElem.textContent.trim();
					console.log('Found name:', place.name);
				} else {
					console.log('No name element found');
					return null;
				}

				// Get rating
				const ratingElem = node.querySelector('span[aria-label*="rating"], span[aria-label*="stars"]');
				if (ratingElem) {
					const ratingText = ratingElem.getAttribute('aria-label');
					console.log('Found rating text:', ratingText);
					const ratingMatch = ratingText.match(/([0-9]+(\.[0-9]+)?)/);
					if (ratingMatch) {
						place.rating = parseFloat(ratingMatch[1]);
						console.log('Parsed rating:', place.rating);
					}
				} else {
					console.log('No rating element found');
				}

				// Get review count
				const reviewsElem = node.querySelector('span[aria-label*="review"]');
				if (reviewsElem) {
					const reviewText = reviewsElem.getAttribute('aria-label') || '';
					console.log('Found review text:', reviewText);
					const reviewMatch = reviewText.match(/([0-9,]+)\s+review/);
					if (reviewMatch) {
						place.review_count = parseInt(reviewMatch[1].replace(/,/g, ''));
						console.log('Parsed review count:', place.review_count);
					}
				} else {
					console.log('No reviews element found');
				}

				// Get all text elements
				const textElems = Array.from(node.querySelectorAll('div[class*="fontBodyMedium"], div[jsaction*="placeCard"]'));
				console.log('Found text elements:', textElems.length);
				
				// Process text elements to find category and address
				let foundCategory = false;
				textElems.forEach((elem, index) => {
					const text = elem.textContent.trim();
					if (!text) return;
					
					if (!foundCategory && text.includes('·')) {
						// This is likely the category line
						const categories = text.split('·').map(cat => cat.trim()).filter(Boolean);
						place.categories = categories;
						if (categories.length > 0) {
							place.category = categories[0];
						}
						foundCategory = true;
						console.log('Found categories:', categories);
					} else if (foundCategory && !place.address) {
						// After finding category, next non-empty line is likely the address
						place.address = text;
						console.log('Found address:', text);
					}
				});

				// Get thumbnail
				const imgElem = node.querySelector('img[src*="photo"], img[src*="place"]');
				if (imgElem) {
					place.thumbnail = imgElem.src;
					console.log('Found thumbnail:', place.thumbnail);
				} else {
					console.log('No thumbnail found');
				}

				// Get price level
				const priceElem = node.querySelector('span[aria-label*="$"]');
				if (priceElem) {
					place.price_range = priceElem.textContent.trim();
					console.log('Found price range:', place.price_range);
				}

				console.log('Final place object:', place);
				return JSON.stringify(place);
			})()
		`, node.FullXPath()), &result),
	)

	if err != nil {
		log.Printf("Error during evaluation: %v", err)
		return nil, fmt.Errorf("failed to extract place data: %w", err)
	}

	if result == "null" || result == "" {
		log.Printf("No result returned from evaluation")
		return nil, nil
	}

	log.Printf("Raw result: %s", result)

	if err := json.Unmarshal([]byte(result), &place); err != nil {
		log.Printf("Error unmarshaling result: %v", err)
		return nil, fmt.Errorf("failed to parse place data: %w", err)
	}

	if place.Name == "" || place.Link == "" {
		log.Printf("Missing required fields: name=%q, link=%q", place.Name, place.Link)
		return nil, nil
	}

	// Generate ID
	if place.Cid != "" {
		place.ID = place.Cid
	} else {
		place.ID = fmt.Sprintf("%x", md5.Sum([]byte(place.Name+place.Address)))
	}

	// Set creation time
	place.CreatedAt = time.Now().Format(time.RFC3339)

	log.Printf("Successfully extracted place: %s", place.Name)
	return &place, nil
}

func (j *PlaceJob) Execute() error {
	// Create a new browser context for this job
	ctx, cancel := j.scraper.newBrowserContext()
	defer cancel()

	log.Printf("Executing place job %s for %s", j.ID(), j.Place.Name)

	// Navigate and wait for the page to load
	if err := j.navigateWithRetry(ctx); err != nil {
		return err
	}

	// Click on the reviews button and sort by newest
	if err := j.openAndSortReviews(ctx); err != nil {
		log.Printf("Error opening reviews: %v", err)
	}

	// Scroll reviews
	if err := j.scrollReviews(ctx); err != nil {
		log.Printf("Error scrolling reviews: %v", err)
	}

	// Extract details
	if err := j.extractDetails(ctx); err != nil {
		return err
	}

	log.Printf("Successfully got details for place: %s (found %d reviews)", j.Place.Name, len(j.Place.Reviews))
	return nil
}

func (j *PlaceJob) navigateWithRetry(ctx context.Context) error {
	var err error
	for i := 0; i < 3; i++ {
		err = chromedp.Run(ctx,
			chromedp.Navigate(j.Place.Link),
			chromedp.WaitVisible(`button[jsaction*="pane.rating.moreReviews"]`, chromedp.ByQuery),
			chromedp.Sleep(2*time.Second),
		)
		if err == nil {
			return nil
		}
		log.Printf("Navigation attempt %d failed: %v", i+1, err)
		time.Sleep(time.Second * time.Duration(i+1))
	}
	return fmt.Errorf("failed to navigate after retries: %w", err)
}

func (j *PlaceJob) openAndSortReviews(ctx context.Context) error {
	// Click reviews button
	if err := chromedp.Run(ctx,
		chromedp.Click(`button[jsaction*="pane.rating.moreReviews"]`, chromedp.ByQuery),
		chromedp.Sleep(2*time.Second),
	); err != nil {
		return fmt.Errorf("failed to click reviews button: %w", err)
	}

	// Click sort button
	if err := chromedp.Run(ctx,
		chromedp.Click(`button[aria-label="Sort reviews"]`, chromedp.ByQuery),
		chromedp.Sleep(1*time.Second),
		chromedp.Click(`span[aria-label="Most recent"]`, chromedp.ByQuery),
		chromedp.Sleep(2*time.Second),
	); err != nil {
		log.Printf("Failed to sort reviews: %v", err)
	}

	return nil
}

func (j *PlaceJob) scrollReviews(ctx context.Context) error {
	// First, ensure we're at the reviews section
	if err := chromedp.Run(ctx, chromedp.WaitVisible(`div[role="dialog"]`, chromedp.ByQuery)); err != nil {
		return fmt.Errorf("reviews dialog not found: %w", err)
	}

	// Improved scrolling logic with better progress tracking
	return chromedp.Run(ctx,
		chromedp.Evaluate(`
			(() => {
				return new Promise((resolve, reject) => {
					const dialog = document.querySelector('div[role="dialog"]');
					if (!dialog) {
						reject('Reviews dialog not found');
						return;
					}

					const reviewsContainer = dialog.querySelector('div[tabindex="-1"]');
					if (!reviewsContainer) {
						reject('Reviews container not found');
						return;
					}

					let lastHeight = 0;
					let noChangeCount = 0;
					const maxNoChange = 3;
					const maxScrolls = 20;
					let scrollCount = 0;

					const scroll = () => {
						reviewsContainer.scrollTo(0, reviewsContainer.scrollHeight);
						const newHeight = reviewsContainer.scrollHeight;

						if (newHeight === lastHeight) {
							noChangeCount++;
						} else {
							noChangeCount = 0;
							lastHeight = newHeight;
						}

						scrollCount++;

						// Continue scrolling if we haven't hit our limits
						if (noChangeCount < maxNoChange && scrollCount < maxScrolls) {
							setTimeout(scroll, 1000);
						} else {
							resolve();
						}
					};

					scroll();
				});
			})()
		`, nil),
	)
}

func (j *PlaceJob) extractDetails(ctx context.Context) error {
	var detailsData string
	err := chromedp.Run(ctx,
		chromedp.Evaluate(`
			(() => {
				const details = {};
				
				// Get website
				const websiteBtn = document.querySelector('a[data-item-id="authority"]');
				if (websiteBtn) {
					details.website = websiteBtn.href;
				}
				
				// Get phone
				const phoneBtn = document.querySelector('button[data-item-id*="phone"]');
				if (phoneBtn) {
					details.phone = phoneBtn.textContent.trim();
				}
				
				// Get coordinates
				const link = document.querySelector('a[href*="/@"]');
				if (link) {
					const coords = link.href.split("/@")[1].split(",");
					details.latitude = parseFloat(coords[0]);
					details.longitude = parseFloat(coords[1]);
				}
				
				// Get opening hours
				const hours = {};
				const hoursRows = document.querySelectorAll('table.WgFkxc tr, table.eK4R0e tr');
				hoursRows.forEach(row => {
					const day = row.querySelector('th');
					const timeSlots = row.querySelector('td');
					if (day && timeSlots) {
						const dayText = day.textContent.trim();
						const slots = timeSlots.textContent.trim().split(',').map(s => s.trim());
						hours[dayText] = slots;
					}
				});
				details.open_hours = hours;
				
				// Get status
				const statusElem = document.querySelector('span[aria-label*="Open"]');
				if (statusElem) {
					details.status = statusElem.getAttribute('aria-label');
				}

				// Get popular times
				const popularTimes = {};
				const daysContainer = document.querySelector('div[aria-label="Popular times"] div[role="img"]');
				if (daysContainer) {
					const days = Array.from(daysContainer.children);
					const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
					days.forEach((day, index) => {
						const hours = Array.from(day.querySelectorAll('div[aria-label]')).map(hour => {
							const label = hour.getAttribute('aria-label');
							const match = label.match(/(\d+)%/);
							return match ? parseInt(match[1]) : 0;
						});
						if (hours.length > 0) {
							popularTimes[dayNames[index]] = hours;
						}
					});
				}
				details.popular_times = popularTimes;

				// Improved review extraction
				const reviews = [];
				const reviewElems = document.querySelectorAll('div.jftiEf');
				reviewElems.forEach(reviewElem => {
					try {
						const review = {};
						
						// Author information
						const authorElem = reviewElem.querySelector('div.d4r55');
						if (authorElem) {
							review.author = authorElem.textContent.trim();
							const authorLink = authorElem.querySelector('a');
							if (authorLink) {
								review.author_link = authorLink.href;
							}
						}
						
						// Rating
						const ratingElem = reviewElem.querySelector('span.kvMYJc');
						if (ratingElem) {
							const ratingText = ratingElem.getAttribute('aria-label');
							const ratingMatch = ratingText.match(/([0-9]+)/);
							if (ratingMatch) {
								review.rating = parseInt(ratingMatch[1]);
							}
						}
						
						// Review text - handle "More" button
						const textElem = reviewElem.querySelector('span.wiI7pd');
						if (textElem) {
							const moreButton = textElem.querySelector('button[aria-label="More"]');
							if (moreButton) {
								moreButton.click();
							}
							review.text = textElem.textContent.trim();
						}
						
						// Time
						const timeElem = reviewElem.querySelector('span.rsqaWe');
						if (timeElem) {
							review.time = timeElem.textContent.trim();
						}

						// Likes
						const likeElem = reviewElem.querySelector('button[aria-label*="likes"]');
						if (likeElem) {
							const likeText = likeElem.getAttribute('aria-label');
							const likeMatch = likeText.match(/(\d+)/);
							if (likeMatch) {
								review.like_count = parseInt(likeMatch[1]);
							}
						}

						// Replies
						const replyElem = reviewElem.querySelector('button[aria-label*="replies"]');
						if (replyElem) {
							const replyText = replyElem.getAttribute('aria-label');
							const replyMatch = replyText.match(/(\d+)/);
							if (replyMatch) {
								review.reply_count = parseInt(replyMatch[1]);
							}
						}

						// Photos
						const photoElems = reviewElem.querySelectorAll('button[jsaction*="reviewPhoto"] img');
						if (photoElems.length > 0) {
							review.photos = Array.from(photoElems).map(img => img.src).filter(Boolean);
						}
						
						if (review.author && review.rating) {
							review.created_at = new Date().toISOString();
							reviews.push(review);
						}
					} catch (err) {
						console.error('Error processing review:', err);
					}
				});
				details.reviews = reviews;
				
				return JSON.stringify(details);
			})()
		`, &detailsData),
	)

	if err != nil {
		return fmt.Errorf("failed to get place details: %w", err)
	}

	var details struct {
		Website      string              `json:"website"`
		Phone        string              `json:"phone"`
		Latitude     float64             `json:"latitude"`
		Longitude    float64             `json:"longitude"`
		OpenHours    map[string][]string `json:"open_hours"`
		Status       string              `json:"status"`
		PopularTimes map[string][]int    `json:"popular_times"`
		Reviews      []Review            `json:"reviews"`
	}

	if err := json.Unmarshal([]byte(detailsData), &details); err != nil {
		return fmt.Errorf("failed to parse details data: %w", err)
	}

	j.Place.Website = details.Website
	j.Place.Phone = details.Phone
	j.Place.Latitude = details.Latitude
	j.Place.Longitude = details.Longitude
	j.Place.OpenHours = details.OpenHours
	j.Place.Status = details.Status
	j.Place.PopularTimes = details.PopularTimes
	j.Place.Reviews = details.Reviews

	return nil
}

func (s *SearchJob) Execute() error {
	// Create a new browser context for this job
	ctx, cancel := s.scraper.newBrowserContext()
	defer cancel()

	url := fmt.Sprintf("https://www.google.com/maps/search/%s/@%f,%f,15z",
		strings.ReplaceAll(s.Query, " ", "+"), s.Lat, s.Lng)
	log.Printf("Starting scrape for URL: %s", url)

	// First, wait for the page to load and scroll to load more results
	if err := chromedp.Run(ctx,
		chromedp.Navigate(url),
		chromedp.WaitVisible(`div[role="feed"]`, chromedp.ByQuery),
		chromedp.Sleep(2*time.Second),
		s.scrollResults(),
		chromedp.Sleep(2*time.Second),
	); err != nil {
		log.Printf("Error during initial page load: %v", err)
		return err
	}

	var nodes []*cdp.Node
	if err := chromedp.Run(ctx,
		chromedp.Nodes(`div[role="feed"] > div > div > a[href*="maps/place"]`, &nodes, chromedp.ByQueryAll),
	); err != nil {
		log.Printf("Error finding place nodes: %v", err)
		return err
	}

	log.Printf("Found %d place nodes", len(nodes))

	var places []Place
	for _, node := range nodes {
		place, err := s.extractPlaceFromNode(ctx, node)
		if err != nil {
			log.Printf("Error extracting place: %v", err)
			continue
		}
		if place != nil {
			places = append(places, *place)
		}
	}

	log.Printf("Successfully extracted %d places", len(places))

	// Store the places in the SearchJob
	s.Places = places

	// Create place jobs for each place
	var wg sync.WaitGroup
	sem := make(chan struct{}, 3) // Limit concurrent jobs to 3

	for i := range places {
		if places[i].Link != "" {
			wg.Add(1)
			go func(place *Place) {
				defer wg.Done()
				sem <- struct{}{}        // Acquire semaphore
				defer func() { <-sem }() // Release semaphore

				placeJob := NewPlaceJob(place, s.scraper)
				s.scraper.AddJob(placeJob)
				if err := placeJob.Execute(); err != nil {
					log.Printf("Error executing place job for %s: %v", place.Name, err)
				}
			}(&places[i])
		}
	}

	wg.Wait()

	// Save results
	result := &SearchResult{
		Places:    places,
		Query:     s.Query,
		Location:  Location{Lat: s.Lat, Lng: s.Lng},
		CreatedAt: time.Now(),
	}

	// Create output directory if it doesn't exist
	if err := os.MkdirAll("output", 0755); err != nil {
		log.Printf("Error creating output directory: %v", err)
		return err
	}

	// Save to file
	filename := fmt.Sprintf("output/places_%s.json", time.Now().Format("20060102_150405"))
	data, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		log.Printf("Error marshaling results: %v", err)
		return err
	}

	if err := os.WriteFile(filename, data, 0644); err != nil {
		log.Printf("Error saving results: %v", err)
		return err
	}

	log.Printf("Successfully saved %d places to %s", len(places), filename)
	return nil
}
