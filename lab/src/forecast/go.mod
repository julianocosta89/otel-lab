module github.com/julianocosta89/otel-lab/forecast

go 1.23.4

require (
    github.com/sirupsen/logrus v1.9.3
    go.opentelemetry.io/contrib/bridges/otellogrus v0.8.0
    go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.58.0
    go.opentelemetry.io/contrib/instrumentation/runtime v0.58.0
    go.opentelemetry.io/otel v1.33.0
    go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc v0.9.0
    go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc v1.33.0
    go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.33.0
    go.opentelemetry.io/otel/log v0.9.0
    go.opentelemetry.io/otel/sdk v1.33.0
    go.opentelemetry.io/otel/sdk/log v0.9.0
    go.opentelemetry.io/otel/sdk/metric v1.33.0
)
