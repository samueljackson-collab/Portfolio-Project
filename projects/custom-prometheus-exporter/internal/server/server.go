package server

import (
	"context"
	"fmt"
	"net/http"
	"time"
)

type Server struct {
	httpServer *http.Server
}

func New(address string, port int, handler http.Handler) *Server {
	srv := &http.Server{
		Addr:              fmt.Sprintf("%s:%d", address, port),
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
	}
	return &Server{httpServer: srv}
}

func (s *Server) Start() error {
	return s.httpServer.ListenAndServe()
}

func (s *Server) Shutdown(ctx context.Context) error {
	return s.httpServer.Shutdown(ctx)
}
