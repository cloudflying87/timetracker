# Cloudflare Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Domain name configured with Cloudflare
- SSL certificates (can use Cloudflare Origin certificates)

## Cloudflare Configuration

### 1. DNS Settings
Set up A records pointing to your server IP:
- `@` (root domain) → Your server IP
- `www` → Your server IP

### 2. SSL/TLS Settings
- Set SSL/TLS encryption mode to "Full (strict)"
- Enable "Always Use HTTPS"
- Enable HSTS (HTTP Strict Transport Security)

### 3. Security Settings
- Enable "Under Attack Mode" if needed
- Configure firewall rules to restrict access
- Enable Bot Fight Mode

### 4. Speed Settings
- Enable "Auto Minify" for CSS, JavaScript, and HTML
- Enable "Brotli" compression
- Configure caching rules for static assets

### 5. Page Rules (optional)
Create page rules for better performance:
- `*.yourdomain.com/static/*` → Cache Everything, Edge Cache TTL: 1 month
- `*.yourdomain.com/media/*` → Cache Everything, Edge Cache TTL: 1 week

## Deployment Steps

### 1. Server Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd TimeTracker

# Create environment file
cp .env.example .env
# Edit .env with your production values
```

### 2. SSL Certificates
Place your SSL certificates in the `ssl/` directory:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - SSL private key

For Cloudflare Origin certificates:
1. Go to SSL/TLS → Origin Server in Cloudflare dashboard
2. Create certificate with your domain
3. Save as cert.pem and key.pem

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Set up hour limits (optional)
docker-compose exec web python manage.py shell
```

### 4. Initial Data Setup
```python
# In Django shell
from timetrack.models import HourLimit
HourLimit.objects.create(period='weekly', max_hours=40)
HourLimit.objects.create(period='monthly', max_hours=160)
```

## Environment Variables (.env)

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=timetracker
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432
```

## Monitoring and Maintenance

### Health Checks
- Monitor application logs: `docker-compose logs -f web`
- Check database health: `docker-compose logs -f db`
- Monitor nginx logs: `docker-compose logs -f nginx`

### Backups
```bash
# Database backup
docker-compose exec db pg_dump -U postgres timetracker > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres timetracker < backup.sql
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

## Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check if Django container is running
2. **Database connection errors**: Verify PostgreSQL is healthy
3. **Static files not loading**: Run `collectstatic` and check nginx config
4. **SSL certificate errors**: Verify certificate files exist and are valid

### Useful Commands
```bash
# View container status
docker-compose ps

# Restart specific service
docker-compose restart web

# View real-time logs
docker-compose logs -f

# Execute commands in container
docker-compose exec web python manage.py shell
```