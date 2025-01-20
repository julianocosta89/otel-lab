# OTel Lab

Below you will find the instructions to guide you through the steps to add visibility
into your services using OpenTelemetry.

## The OpenTelemetry Collector

First, let's configure thr OpenTelemtry Collector to receive, process and export
telemetry data.

1. Open the file [src/otel-collector/otel-collector-config.yaml](src/otel-collector/otel-collector-config.yaml).
You will notice that there are 5 sections in the `config` file:
    - `receivers`: collect telemetry from one or more sources.
    - `processors`: take the data collected by receivers and modify or transform it before sending
    it to the exporters.
    - `connectors`: consumes data as an exporter at the end of one pipeline and emits data as a receiver at the
    beginning of another pipeline.
    - `exporters`: send data to one or more backends or destinations.
    - `service`: is used to configure what components are enabled in the Collector based on the
    configuration found in the receivers, processors, exporters, and extensions sections
1. Configuring the `receivers`:
    - To configure the Collector to receive OTLP data in the gRPC and HTTP protocols, we need the following:

        ```yaml
        otlp:
          protocols:
            grpc:
              endpoint: ${env:OTEL_COLLECTOR_HOST}:${env:OTEL_COLLECTOR_PORT_GRPC}
            http:
              endpoint: ${env:OTEL_COLLECTOR_HOST}:${env:OTEL_COLLECTOR_PORT_HTTP}
        ```

1. Configuring the `processors`:
    - To better compress the data and reduce the number of outgoing connections required to transmit the data, let's
    use the `batch` processor:

        ```yaml
        batch: {}
        ```

1. 
