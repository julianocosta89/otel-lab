# OTel Lab

Below you will find the instructions to guide you through the steps to add visibility
into your services using OpenTelemetry.

## The OpenTelemetry Collector

First, let's configure thr OpenTelemetry Collector to receive, process and export
telemetry data.

Follow the instructions on [src/otel-collector/README.md](src/otel-collector/README.md).

## Instrumenting Weather Service

Now let's instrument the `weather` service.

The service is written in Python and it's the entrypoint of our application.

Follow the instructions on [src/weather/README.md](src/weather/README.md) to add
OpenTelemetry to the service.
