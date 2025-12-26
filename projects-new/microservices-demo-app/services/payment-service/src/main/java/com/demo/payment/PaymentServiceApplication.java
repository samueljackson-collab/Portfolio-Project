package com.demo.payment;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@SpringBootApplication
public class PaymentServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(PaymentServiceApplication.class, args);
    }
}

@RestController
class PaymentController {
    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok", "service", "payment-service");
    }

    @PostMapping("/payments")
    @CircuitBreaker(name = "bankGateway", fallbackMethod = "fallback")
    public Map<String, String> processPayment() {
        if (Math.random() < 0.3) {
            throw new RuntimeException("Bank gateway timeout");
        }
        return Map.of("status", "processed");
    }

    public Map<String, String> fallback(Throwable throwable) {
        return Map.of("status", "degraded", "reason", throwable.getMessage());
    }
}
