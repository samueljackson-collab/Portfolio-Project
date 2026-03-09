FROM gradle:8-jdk17 AS build
WORKDIR /app
COPY build.gradle settings.gradle ./
COPY src ./src
RUN gradle bootJar --no-daemon

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/build/libs/payment-service-0.1.0.jar /app/payment-service.jar
EXPOSE 8084
CMD ["java", "-jar", "/app/payment-service.jar"]
