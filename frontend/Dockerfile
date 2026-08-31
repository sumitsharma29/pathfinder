# Step 1: Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build production bundle
RUN npm run build

# Step 2: Production serve stage
FROM nginx:alpine-slim

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
