FROM node:25-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --production

FROM node:25-alpine
WORKDIR /app
COPY --from=base /app/node_modules ./node_modules
COPY src ./src
COPY package.json ./package.json
ENV PORT=8081
EXPOSE 8081
CMD ["npm", "start"]
