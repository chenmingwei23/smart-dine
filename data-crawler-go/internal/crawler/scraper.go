package crawler

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/chromedp/chromedp"
)

type Scraper struct {
	allocCtx    context.Context
	allocCancel context.CancelFunc
	mu          sync.Mutex
	jobs        map[string]Job
}

func NewScraper() *Scraper {
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
		chromedp.Flag("remote-debugging-port", "9222"),
		chromedp.Flag("window-size", "1920,1080"),
		chromedp.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
	)

	log.Println("Creating Chrome allocator context...")
	allocCtx, allocCancel := chromedp.NewExecAllocator(context.Background(), opts...)

	log.Println("Creating browser context...")
	ctx, _ := chromedp.NewContext(
		allocCtx,
		chromedp.WithLogf(log.Printf),
		chromedp.WithDebugf(log.Printf),
	)

	log.Println("Starting browser...")
	if err := chromedp.Run(ctx); err != nil {
		log.Printf("Error starting browser: %v", err)
	}

	log.Println("Chrome initialization completed successfully")
	return &Scraper{
		allocCtx:    allocCtx,
		allocCancel: allocCancel,
		jobs:        make(map[string]Job),
	}
}

func (s *Scraper) Close() {
	if s.allocCancel != nil {
		s.allocCancel()
	}
}

func (s *Scraper) AddJob(job Job) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.jobs[job.ID()] = job
}

func (s *Scraper) GetJob(id string) Job {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.jobs[id]
}

func (s *Scraper) newBrowserContext() (context.Context, context.CancelFunc) {
	log.Println("Creating new browser context...")
	ctx, cancel := context.WithTimeout(s.allocCtx, 5*time.Minute)
	browserCtx, _ := chromedp.NewContext(ctx,
		chromedp.WithLogf(log.Printf),
		chromedp.WithDebugf(log.Printf),
	)

	log.Println("Starting browser...")
	if err := chromedp.Run(browserCtx); err != nil {
		log.Printf("Error ensuring browser is ready: %v", err)
	}

	log.Println("Browser context created successfully")
	return browserCtx, cancel
}

func (s *Scraper) Run(query string, lat, lng float64) ([]Place, error) {
	log.Printf("Starting scraper for query: %s at location: %f,%f", query, lat, lng)

	// Create and execute a new search job
	searchJob := &SearchJob{
		Query:   query,
		Lat:     lat,
		Lng:     lng,
		scraper: s,
	}

	s.AddJob(searchJob)
	err := searchJob.Execute()
	if err != nil {
		return nil, err
	}

	// Get the places from the search result
	if job := s.GetJob(searchJob.ID()); job != nil {
		if searchJob, ok := job.(*SearchJob); ok {
			return searchJob.Places, nil
		}
	}

	return nil, fmt.Errorf("failed to get search results")
}
