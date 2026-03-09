.PHONY: run test lint

run:
	go run ./cmd/exporter -config configs/config.example.yaml

test:
	go test ./...

lint:
	golangci-lint run ./...
