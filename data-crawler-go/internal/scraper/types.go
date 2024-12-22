package scraper

import "regexp"

// Place represents a restaurant or business place from Google Maps
type Place struct {
	Name        string   `json:"name"`
	Link        string   `json:"link"`
	CID         string   `json:"cid"`
	Rating      float64  `json:"rating,omitempty"`
	ReviewCount int      `json:"review_count,omitempty"`
	Category    string   `json:"category,omitempty"`
	Categories  []string `json:"categories,omitempty"`
	Address     string   `json:"address,omitempty"`
	Thumbnail   string   `json:"thumbnail,omitempty"`
	PriceRange  string   `json:"price_range,omitempty"`
}

var (
	cidRegex         = regexp.MustCompile(`0x[0-9a-fA-F]+:`)
	ratingRegex      = regexp.MustCompile(`([0-9]+(\.[0-9]+)?)`)
	reviewCountRegex = regexp.MustCompile(`([0-9,]+)\s+review`)
)
