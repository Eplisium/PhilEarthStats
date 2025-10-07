# Multi-stage Docker build for PhilEarthStats

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + Serve
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/*.py ./
COPY backend/instance ./instance

# Copy built frontend to static directory
COPY --from=frontend-build /app/frontend/dist ./static

# Create directory for SQLite database
RUN mkdir -p /app/instance && chmod 755 /app/instance

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV SQLALCHEMY_DATABASE_URI=sqlite:///instance/earthquakes.db

# Health check using curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
