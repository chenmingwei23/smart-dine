package crawler

import (
	"encoding/json"
	"fmt"
	"time"
)

type Job interface {
	ID() string
	Execute() error
}

type SearchJob struct {
	Query     string    `json:"query"`
	Lat       float64   `json:"lat"`
	Lng       float64   `json:"lng"`
	CreatedAt time.Time `json:"created_at"`
	Places    []Place   `json:"places"`
	jobID     string
	scraper   *Scraper
}

func NewSearchJob(query string, lat, lng float64, scraper *Scraper) *SearchJob {
	return &SearchJob{
		Query:     query,
		Lat:       lat,
		Lng:       lng,
		CreatedAt: time.Now(),
		jobID:     fmt.Sprintf("search_%d", time.Now().UnixNano()),
		scraper:   scraper,
	}
}

func (j *SearchJob) ID() string {
	return j.jobID
}

type Place struct {
	ID           string              `json:"id"`
	Cid          string              `json:"cid"`
	Link         string              `json:"link"`
	Name         string              `json:"name"`
	Categories   []string            `json:"categories"`
	Category     string              `json:"category"`
	Address      string              `json:"address"`
	OpenHours    map[string][]string `json:"open_hours"`
	PopularTimes map[string][]int    `json:"popular_times"`
	Website      string              `json:"website"`
	Phone        string              `json:"phone"`
	PlusCode     string              `json:"plus_code"`
	ReviewCount  int                 `json:"review_count"`
	Rating       float64             `json:"rating"`
	Latitude     float64             `json:"latitude"`
	Longitude    float64             `json:"longitude"`
	Status       string              `json:"status"`
	PriceRange   string              `json:"price_range"`
	Description  string              `json:"description"`
	Reviews      []Review            `json:"reviews"`
	Thumbnail    string              `json:"thumbnail"`
	CreatedAt    string              `json:"created_at"`
}

type Review struct {
	Author     string   `json:"author"`
	AuthorLink string   `json:"author_link"`
	Rating     int      `json:"rating"`
	Text       string   `json:"text"`
	Time       string   `json:"time"`
	Language   string   `json:"language"`
	LikeCount  int      `json:"like_count"`
	ReplyCount int      `json:"reply_count"`
	Images     []string `json:"images"`
	CreatedAt  string   `json:"created_at"`
}

type PlaceJob struct {
	Place     *Place    `json:"place"`
	CreatedAt time.Time `json:"created_at"`
	jobID     string
	scraper   *Scraper
}

func NewPlaceJob(place *Place, scraper *Scraper) *PlaceJob {
	return &PlaceJob{
		Place:     place,
		CreatedAt: time.Now(),
		jobID:     fmt.Sprintf("place_%s_%d", place.ID, time.Now().UnixNano()),
		scraper:   scraper,
	}
}

func (j *PlaceJob) ID() string {
	return j.jobID
}

type SearchResult struct {
	Places    []Place   `json:"places"`
	Query     string    `json:"query"`
	Location  Location  `json:"location"`
	CreatedAt time.Time `json:"created_at"`
}

type Location struct {
	Lat float64 `json:"lat"`
	Lng float64 `json:"lng"`
}

func (p *Place) MarshalJSON() ([]byte, error) {
	type Alias Place
	return json.Marshal(&struct {
		*Alias
		CreatedAt string `json:"created_at"`
	}{
		Alias:     (*Alias)(p),
		CreatedAt: p.CreatedAt,
	})
}

func (p *Place) UnmarshalJSON(data []byte) error {
	type Alias Place
	aux := &struct {
		*Alias
		CreatedAt string `json:"created_at"`
	}{
		Alias: (*Alias)(p),
	}
	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}
	if aux.CreatedAt == "" {
		p.CreatedAt = time.Now().Format(time.RFC3339)
	} else {
		p.CreatedAt = aux.CreatedAt
	}
	return nil
}
