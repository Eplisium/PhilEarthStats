# Docker Quick Start Guide

This is a quick reference for running PhilEarthStats with Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (optional but recommended)

## Quick Start with Docker Compose

```bash
# 1. Clone the repository
git clone <repository-url>
cd PhilEarthStats

# 2. (Optional) Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENROUTER_API_KEY if you want AI features

# 3. Build and run
docker-compose up -d

# 4. Access the application
# Open your browser to http://localhost:5000

# 5. View logs
docker-compose logs -f app

# 6. Stop the application
docker-compose down
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI analysis | None | No (but needed for AI features) |
| `FLASK_ENV` | Flask environment (development/production) | production | No |
| `CACHE_TIMEOUT` | Cache timeout in seconds | 300 | No |

## Data Persistence

The application uses a Docker volume to persist earthquake data between container restarts:

```bash
# View volumes
docker volume ls

# Inspect the earthquake data volume
docker volume inspect philearthstats_earthquake-data

# Remove volume (deletes all earthquake data)
docker-compose down -v
```

## Useful Commands

```bash
# Rebuild the image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# View container status
docker-compose ps

# View resource usage
docker stats

# Execute commands in running container
docker-compose exec app sh

# View application logs
docker-compose logs -f app

# Restart the application
docker-compose restart app
```

## Troubleshooting

### Health Check Failing

```bash
# Check if the container is running
docker-compose ps

# View logs for errors
docker-compose logs app

# Test health endpoint manually
docker-compose exec app curl -f http://localhost:5000/api/health
```

### Port Already in Use

If port 5000 is already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Change 8080 to any available port
```

### Rebuilding After Code Changes

```bash
# Stop, rebuild, and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Issues

```bash
# Reset database by removing volume
docker-compose down -v
docker-compose up -d
```

## Production Considerations

1. **Always set OPENROUTER_API_KEY** as environment variable (not in .env file committed to git)
2. **Use a reverse proxy** (Nginx/Apache) for SSL/TLS termination
3. **Enable firewall** and only expose necessary ports
4. **Regular backups** of the earthquake-data volume
5. **Monitor logs** for errors and performance issues
6. **Scale workers** by modifying the `--workers` parameter in Dockerfile

## Next Steps

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for local development setup
- See [README.md](README.md) for application documentation
