FROM gradle:9-jdk17 AS build
WORKDIR /app
COPY build.gradle settings.gradle ./
COPY src ./src
RUN gradle bootJar --no-daemon

FROM eclipse-temurin:25-jre-alpine
WORKDIR /app
COPY --from=build /app/build/libs/payment-service-0.1.0.jar /app/payment-service.jar
EXPOSE 8084
CMD ["java", "-jar", "/app/payment-service.jar"]
