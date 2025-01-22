# OTel Lab

This lab was created to demonstrate OpenTelemetry.

The [lab](lab) folder contains the blueprint of all services, as well as an empty
configuration of the OpenTelemetry Collector.

It also contains a step-by-step `README` that will guide you through the instrumentation
and configuration process.

The [solution](solution) folder contains the final state of the lab, with all services
instrumented and OpenTelemetry Collector configured.

## Lab Details

The Lab contains an application composed of 2 services, plus a Postgres database:

- Weather (Python) - Users can query the weather for a specific location.
  - The service exposes 2 endpoints:
    - `/weather/<location>/<country>`
      - eg: <http://localhost:8080/weather/Linz/Austria>
    - `/weather/coordinates/<latitude>/<longitude>`
      - eg: <http://localhost:8080/weather/coordinates/48.3059078/14.286198>
- Forecast (Go) - Receives a call from `Weather` and returns the forecast for
the requested location.
  - It is only accessible by containers running on the same network. Not exposed
  publicly.
- Coordinates-DB (Postgres) - Stores coordinates for locations already queried by
the user.

It also contains some tools that will help you navigate the data:

- OpenTelemetry Collector (otelcol):
  - The Collector receives traces, metrics, and logs as OTLP data from the `weather`
  and `forecast` services, as well as queries the [PostgreSQL statistics collector][1].
  - It processes the data and exports it as OTLP data to Jaeger (traces) and Aspire
  (traces, metrics, and logs).
- Jaeger is used to receive and visualize traces:
  - Accessible at: <http://localhost:16686/>
- Aspire Dashboard is used to receive and visualize traces, metrics, and logs:
  - Accessible at: <http://localhost:18888/>

## Lab Diagram

```mermaid
flowchart LR
    classDef golang fill:#ff9500,color:black;
    classDef python fill:#4ab52f,color:white;
    classDef jaeger fill:#00e5ff,color:black;
    classDef otelcol fill:#ffd500,color:black;
    classDef aspire fill:#8000ff,color:white;
    classDef unmonitored fill:#ffffff,color:black;

    subgraph Service Legend
    golang(Go):::golang
    python(Python):::python
    unmonitored:::unmonitored
    end

    subgraph Service Diagram
        weather(weather):::python
        forecast(forecast):::golang
        coordinates[(coordinates-db<br/>PostgreSQL)]
        otelcol{otelcol}:::otelcol
        jaeger[jaeger]:::jaeger
        aspire[aspire]:::aspire

        user@{ shape: stadium}-->weather--->forecast
        weather--GET-->openstreetmap:::unmonitored

        forecast--GET-->api.open-meteo:::unmonitored

        weather--Traces | Metrics | Logs-->otelcol
        weather-->coordinates
        
        forecast--Traces | Metrics | Logs-->otelcol

        otelcol--Traces-->jaeger
        otelcol--Traces | Metrics | Logs-->aspire
        otelcol--Queries statistics-->coordinates
    end
```

[1]: https://www.postgresql.org/docs/13/monitoring-stats.html