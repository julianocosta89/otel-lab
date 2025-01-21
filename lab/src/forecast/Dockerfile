FROM golang:1.23.4-alpine as base


FROM base as dev
WORKDIR /usr/src/app/
COPY go.mod ./
RUN go mod download


FROM base as builder
WORKDIR /usr/src/app/
COPY --from=dev /usr/src/app/go.mod /usr/src/app/go.sum ./
RUN go mod download
COPY . .
RUN go get
RUN go build -ldflags "-s -w" -o /go/bin/forecast/ ./


FROM alpine AS release
WORKDIR /usr/src/app/
COPY --from=builder /go/bin/forecast/ ./
EXPOSE ${FORECAST_PORT}
ENTRYPOINT [ "./forecast" ]
