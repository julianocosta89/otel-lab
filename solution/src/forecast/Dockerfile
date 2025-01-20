FROM golang:1.23.4-alpine as builder

WORKDIR /usr/src/app/

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -ldflags "-s -w" -o /go/bin/forecast/ ./


FROM alpine AS release

WORKDIR /usr/src/app/
COPY --from=builder /go/bin/forecast/ ./

EXPOSE ${FORECAST_PORT}
ENTRYPOINT [ "./forecast" ]
