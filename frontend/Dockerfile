# Multi-stage Dockerfile for React frontend

# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./

RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

# Stage 2: Hardened runtime
FROM nginxinc/nginx-unprivileged:1.27-alpine

USER root
RUN apk add --no-cache curl \
    && rm -rf /var/cache/apk/*
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

USER 101
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
