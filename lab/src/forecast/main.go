package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"time"

	log "github.com/sirupsen/logrus"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/contrib/instrumentation/runtime"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type ForecastResponse struct {
	Latitude         float64 `json:"latitude"`
	Longitude        float64 `json:"longitude"`
	GenerationTimeMs float64 `json:"generationtime_ms"`
	UtcOffsetSeconds int     `json:"utc_offset_seconds"`
	Timezone         string  `json:"timezone"`
	TimezoneAbbrev   string  `json:"timezone_abbreviation"`
	Elevation        float64 `json:"elevation"`
	DailyUnits       struct {
		Time             string `json:"time"`
		Temperature2mMax string `json:"temperature_2m_max"`
		Temperature2mMin string `json:"temperature_2m_min"`
		DaylightDuration string `json:"daylight_duration"`
	} `json:"daily_units"`
	Daily struct {
		Time             []string  `json:"time"`
		Temperature2mMax []float64 `json:"temperature_2m_max"`
		Temperature2mMin []float64 `json:"temperature_2m_min"`
		DaylightDuration []float64 `json:"daylight_duration"`
	} `json:"daily"`
}

func getForecast(latitude, longitude string, ctx context.Context) (*ForecastResponse, error) {
	url := fmt.Sprintf("https://api.open-meteo.com/v1/forecast?daily=temperature_2m_max,temperature_2m_min,daylight_duration&timezone=Europe%%2FBerlin&forecast_days=1&latitude=%s&longitude=%s", latitude, longitude)
	log.WithContext(ctx).Infof("Getting forecast from %s", url)

	client := http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}
	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to get forecast: %s", resp.Status)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var forecast ForecastResponse
	if err := json.Unmarshal(body, &forecast); err != nil {
		return nil, err
	}

	return &forecast, nil
}

func forecastHandler(w http.ResponseWriter, r *http.Request) {
	latitude := r.URL.Query().Get("latitude")
	longitude := r.URL.Query().Get("longitude")
	if latitude == "" || longitude == "" {
		log.Println("latitude and longitude are required")
		http.Error(w, "latitude and longitude are required", http.StatusBadRequest)
		return
	}

	span := trace.SpanFromContext(r.Context())

	span.SetAttributes(
		attribute.String("latitude", latitude),
		attribute.String("longitude", longitude),
	)

	forecast, err := getForecast(latitude, longitude, r.Context())
	if err != nil {
		log.Printf("failed to get forecast: %s", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	msg := fmt.Sprintf("Elevation Found: %.2f", forecast.Elevation)
	span.AddEvent(msg)

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(forecast); err != nil {
		log.Printf("failed to encode forecast: %s", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func main() {
	// Handle SIGINT (CTRL+C) gracefully.
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	// Set up OpenTelemetry.
	otelShutdown, err := setupOTelSDK(ctx)
	if err != nil {
		return
	}
	// Handle shutdown properly so nothing leaks.
	defer func() {
		err = errors.Join(err, otelShutdown(context.Background()))
	}()

	err = runtime.Start(runtime.WithMinimumReadMemStatsInterval(time.Second))
	if err != nil {
		log.Fatal(err)
	}

	log.SetFormatter(&log.JSONFormatter{})

	otelHandler := otelhttp.NewHandler(http.HandlerFunc(forecastHandler), "forecast")
	http.Handle("/forecast", otelHandler)

	port := os.Getenv("FORECAST_PORT")
	if port == "" {
		port = "9090"
	}
	log.Printf("Starting forecast service on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("could not start server: %s", err)
	}
}
