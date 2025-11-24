# Multi-stage Dockerfile for React frontend with hardened runtime
FROM node:18-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
    && apk add --no-cache curl

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
RUN chown -R appuser:appgroup /usr/share/nginx/html

USER appuser
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost || exit 1

CMD ["nginx", "-g", "daemon off;"]
