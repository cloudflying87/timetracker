# Production Deployment Guide

## Cloudflare Tunnel Setup

### 1. Create Cloudflare Tunnel
1. Go to Cloudflare Dashboard → Zero Trust → Access → Tunnels
2. Create a new tunnel (name it something like "timetracker")
3. Copy the tunnel token

### 2. Configure Environment
```bash
cp .env.production .env
# Edit .env with your actual values:
# - SECRET_KEY (generate a new one)
# - DEBUG=False
# - ALLOWED_HOSTS (your domain)
# - DB_NAME, DB_USER, DB_PASSWORD (database settings)
# - CLOUDFLARE_TUNNEL_TOKEN (from step 1)
```

### 3. Update Cloudflare Config
Edit `cloudflared/config.yml`:
- Replace `timetracker` with your actual tunnel name (or keep it)
- Replace `timetracker.flyhomemnlab.com` with your actual domain

### 4. Create Tunnel Credentials
You'll need to get the credentials file from Cloudflare:
1. Install cloudflared locally: `brew install cloudflared` (Mac) or download from Cloudflare
2. Login to Cloudflare: `cloudflared tunnel login`
3. Create tunnel: `cloudflared tunnel create timetracker`
4. Copy the generated credentials file to `./cloudflared/credentials.json`
5. Get your tunnel token from Cloudflare dashboard and add to `.env`

## Deployment Commands

### Option 1: With Cloudflare Tunnel (Recommended)
```bash
# Ensure .env file is configured
cp .env.production .env
# Edit .env with your actual values

# Start all services including Cloudflare tunnel
docker-compose up -d

# Wait for containers to start
sleep 30

# The database migrations are run automatically by the web container
# But you can run additional setup:

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Or use the build script for complete setup
./build.sh -p
```

### Option 2: Traditional Server with SSL
If you prefer traditional hosting:
1. Remove the `cloudflared` service from docker-compose.yml
2. Get SSL certificates and place in `./ssl/` directory
3. Update nginx.conf with your domain
4. Deploy to your server

### Option 3: Using Build Script (Easiest)
```bash
# Copy environment file
cp .env.production .env
# Edit .env with your values

# Use build script for complete deployment
./build.sh -y  # Deploy to production
# OR
./build.sh -p  # Initial setup only
```

## Post-Deployment Setup

### 1. Admin User Setup
```bash
# Make your user a staff member for admin access
docker-compose exec web python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
user.is_staff = True
user.save()
```

### 2. Configure Pay Rates
1. Go to `/admin/` 
2. Add pay rates for users under "Pay rates"
3. Configure hour limits under "Hour limits"

### 3. Test the Application
- Main app: Your domain
- Admin panel: Your domain/admin/
- Admin dashboard: Your domain/admin-dashboard/

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f cloudflared
```

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U postgres timetracker > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U postgres timetracker < backup_20241212.sql
```

## Troubleshooting

### Common Issues
1. **Admin button not showing**: User needs `is_staff = True`
2. **Cloudflare tunnel not connecting**: Check tunnel token and credentials
3. **Database connection errors**: Check DB_PASSWORD in .env
4. **Static files not loading**: Run `docker-compose exec web python manage.py collectstatic`

### Security Checklist
- [ ] Changed SECRET_KEY from default
- [ ] Set DEBUG=False
- [ ] Updated ALLOWED_HOSTS
- [ ] Strong database password
- [ ] Regular backups scheduled
- [ ] SSL/HTTPS enabled
- [ ] Cloudflare security features enabled

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| SECRET_KEY | Yes | Django secret key (generate new one) |
| DEBUG | Yes | Set to False for production |
| ALLOWED_HOSTS | Yes | Comma-separated list of allowed domains |
| DB_NAME | Yes | Database name (timetracker) |
| DB_USER | Yes | Database user (postgres) |
| DB_PASSWORD | Yes | PostgreSQL password |
| DB_HOST | Yes | Database host (db for Docker) |
| DB_PORT | Yes | Database port (5432) |
| POSTGRES_DB | Yes | Same as DB_NAME (for postgres container) |
| POSTGRES_USER | Yes | Same as DB_USER (for postgres container) |
| POSTGRES_PASSWORD | Yes | Same as DB_PASSWORD (for postgres container) |
| CLOUDFLARE_TUNNEL_TOKEN | Yes | From Cloudflare tunnel setup |
| EMAIL_HOST_USER | No | For email notifications |
| EMAIL_HOST_PASSWORD | No | Email app password |