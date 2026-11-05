# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

# Browser-facing API URL. The host publishes the API on 13800; containers keep 8000.
# Override with --build-arg when HOST_BACKEND_PORT changes, then rebuild this image.
ARG PUBLIC_API_URL=http://localhost:13800
ARG VITE_API_URL=http://localhost:13800
ENV PUBLIC_API_URL=$PUBLIC_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Production image, copy all the files and run the app
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

# Install Python for build time script and PostgreSQL dependencies
RUN apk add --no-cache python3 py3-pip postgresql-client \
    gcc musl-dev postgresql-dev python3-dev
RUN pip3 install --break-system-packages psycopg2-binary

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 sveltekit

# Copy the built application
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json

# Copy static assets
COPY --from=builder /app/static ./static

# Copy build time script
COPY scripts/write_build_time.py ./write_build_time.py

# Create startup script that writes start time and starts the app
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "Writing start time to database..."' >> /app/start.sh && \
    echo 'export POSTGRES_HOST=db' >> /app/start.sh && \
    echo 'export POSTGRES_USER=postgres' >> /app/start.sh && \
    echo 'export POSTGRES_PASSWORD=postgres' >> /app/start.sh && \
    echo 'export POSTGRES_DB=sannetic_explorer' >> /app/start.sh && \
    echo 'python3 /app/write_build_time.py frontend start || echo "Failed to write start time"' >> /app/start.sh && \
    echo 'echo "Starting frontend application..."' >> /app/start.sh && \
    echo 'exec node build' >> /app/start.sh && \
    chmod +x /app/start.sh

USER sveltekit

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Database connection environment variables
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=sannetic_explorer
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres123

# Start the application with build time logging
CMD ["/app/start.sh"] 