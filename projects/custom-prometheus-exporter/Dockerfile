FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/custom-exporter ./cmd/exporter

FROM alpine:3.23
RUN addgroup -S exporter && adduser -S exporter -G exporter
USER exporter
WORKDIR /app
COPY --from=build /bin/custom-exporter /app/custom-exporter
COPY configs/config.example.yaml /app/config.yaml
EXPOSE 9108
ENTRYPOINT ["/app/custom-exporter", "-config", "/app/config.yaml"]
