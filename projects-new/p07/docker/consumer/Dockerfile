FROM golang:1.21-alpine
WORKDIR /app
COPY consumer.go .
RUN go mod init roaming-consumer && \
    go get github.com/segmentio/kafka-go && \
    go build -o consumer consumer.go
EXPOSE 9102
ENTRYPOINT ["/app/consumer"]
