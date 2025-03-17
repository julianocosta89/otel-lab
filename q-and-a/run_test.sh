#!/bin/bash

echo "Cleaning up file storage to start fresh"
rm -rf otel-collector/file_storage

echo "Starting the demo services"
docker compose up -d
echo "Docker compose started."

echo ""
echo "Sleep for 5 seconds"
for i in {1..5}; do
    sleep 1
    echo -n "."
done

echo ""
echo "Sending 100 concurrent requests to the Collector"
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
echo ""
echo "Waiting for 15 seconds before killing the Collector"

for i in {1..15}; do
    sleep 1
    echo -n "."
done

echo ""
echo "Killing the Collector"

# Kill the container
docker kill q-and-a-otel-collector-1
echo "Collector killed."

echo ""
echo "Navigate to the backend to view that no data was sent."
echo "Jaeger: http://localhost:16686"
echo "Aspire: http://localhost:18888"

echo ""
echo "Whenever ready, run the following command to start the Collector again (add \`-d\` to run in background):"
echo "docker compose up otel-collector"

echo ""
echo "After the Collector is running again, navigate to the backend to view that data is being sent (it should take a couple of seconds)."