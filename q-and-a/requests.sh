#!/bin/bash

# Function to generate random latitude and longitude
generate_coordinates() {
    latitude=$(awk -v min=-90 -v max=90 'BEGIN{srand(); print min+rand()*(max-min)}')
    longitude=$(awk -v min=-180 -v max=180 'BEGIN{srand(); print min+rand()*(max-min)}')
    echo "$latitude $longitude"
}

# Loop to send 100 concurrent requests
for i in {1..100}; do
    coords=($(generate_coordinates))
    latitude=${coords[0]}
    longitude=${coords[1]}

    # Send the request without waiting for response
    curl -s "http://localhost:8080/weather/coordinates/$latitude/$longitude" > /dev/null &

    echo "Request $i sent to http://localhost:8080/weather/coordinates/$latitude/$longitude"
done

echo "All 100 requests sent concurrently."
