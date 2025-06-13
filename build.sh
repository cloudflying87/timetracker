#!/bin/bash

# TimeTracker Build Script
# Handles backup, rebuild, migration, and deployment operations

# Default values
BACKUP_all=false
BACKUP_data=false
BACKUP_local=false
REBUILD=false
SOFT_REBUILD=false
RESTORE=false
ALL=false
MIGRATE=false
DOWNLOAD=false
SETUP=false
DEPLOY=false

# Function to display help
show_help() {
    echo "TimeTracker Build Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -d, --date DATE   Date for database filenames (required for backup/restore operations)"
    echo "  -a, --all         Run all steps (backup, rebuild, migrate, restore)"
    echo "  -b, --backup      Only backs up data.sql"
    echo "  -t, --backupall   Backs up all database types (data, schema, clean)"
    echo "  -l, --local       Local backup without Docker"
    echo "  -r, --rebuild     Full rebuild (stop, remove, prune, includes migrate)"
    echo "  -s, --soft        Soft rebuild (preserves database, git pull, migrate)"
    echo "  -o, --restore     Restore database from backup"
    echo "  -m, --migrate     Run Django migrations only"
    echo "  -w, --download    Download backup from remote server"
    echo "  -p, --setup       Initial setup (create superuser, hour limits)"
    echo "  -y, --deploy      Deploy to production"
    echo ""
    echo "Examples:"
    echo "  $0 -d 2023-05-13 -b       # Backup with date"
    echo "  $0 -r                     # Full rebuild"
    echo "  $0 -s                     # Soft rebuild with git pull"
    echo "  $0 -m                     # Run migrations only"
    echo "  $0 -p                     # Initial setup"
    echo "  $0 -y                     # Deploy to production"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--date)
            USER_DATE="$2"
            shift 2
            ;;
        -a|--all)
            ALL=true
            shift
            ;;
        -b|--backup)
            BACKUP_data=true
            shift
            ;;
        -t|--backupall)
            BACKUP_all=true
            shift
            ;;
        -l|--local)
            BACKUP_local=true
            shift
            ;;
        -r|--rebuild)
            REBUILD=true
            shift
            ;;
        -s|--soft)
            SOFT_REBUILD=true
            shift
            ;;
        -o|--restore)
            RESTORE=true
            shift
            ;;
        -m|--migrate)
            MIGRATE=true
            shift
            ;;
        -w|--download)
            DOWNLOAD=true
            shift
            ;;
        -p|--setup)
            SETUP=true
            shift
            ;;
        -y|--deploy)
            DEPLOY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If ALL is set, enable relevant options
if [ "$ALL" = true ]; then
    BACKUP_all=true
    REBUILD=true
    RESTORE=true
    MIGRATE=true
fi

# If SOFT_REBUILD is set, enable migrate
if [ "$SOFT_REBUILD" = true ]; then
    MIGRATE=true
fi

# If REBUILD is set, enable migrate
if [ "$REBUILD" = true ]; then
    MIGRATE=true
fi

# Check if date is provided when needed
if [[ ("$BACKUP_data" = true || "$BACKUP_all" = true || "$BACKUP_local" = true || "$RESTORE" = true || "$DOWNLOAD" = true) && -z "$USER_DATE" ]]; then
    echo "Error: Date (-d or --date) is required for backup/restore/download operations"
    show_help
    exit 1
fi

# Set default date format if needed
if [ -z "$USER_DATE" ]; then
    USER_DATE=$(date +%Y-%m-%d)
fi

# Display selected operations
echo "TimeTracker Build Script"
echo "========================"
echo "Date: $USER_DATE"
echo "Backup Data: $BACKUP_data"
echo "Backup All: $BACKUP_all"
echo "Backup Local: $BACKUP_local"
echo "Rebuild: $REBUILD"
echo "Soft Rebuild: $SOFT_REBUILD"
echo "Restore: $RESTORE"
echo "Migrate: $MIGRATE"
echo "Download: $DOWNLOAD"
echo "Setup: $SETUP"
echo "Deploy: $DEPLOY"
echo "-----------------------------------"

# Project specific settings
PROJECT_NAME="timetracker"
DB_CONTAINER="timetracker-db-1"
WEB_CONTAINER="timetracker-web-1"
NGINX_CONTAINER="timetracker-nginx-1"
CLOUDFLARED_CONTAINER="timetracker-cloudflared-1"
DB_NAME="timetracker"
DB_USER="postgres"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    if [ -f ".env.production" ]; then
        echo "Copying .env.production to .env"
        cp .env.production .env
    else
        echo "Please create a .env file from .env.example"
        exit 1
    fi
fi

# Backup database (data only)
if [ "$BACKUP_data" = true ]; then
    echo "Taking database backup with data only: $USER_DATE"
    
    # Create backup directory if it doesn't exist
    mkdir -p ./backups
    
    # Check if container is running
    if ! docker ps | grep -q $DB_CONTAINER; then
        echo "Database container is not running. Starting containers..."
        sudo docker compose up -d db
        sleep 10
    fi
    
    sudo docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME -a -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql
    echo "Backup saved to: ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql"
fi

# Backup database (all formats)
if [ "$BACKUP_all" = true ]; then
    echo "Backing up database in all formats: $USER_DATE"
    
    # Create backup directory if it doesn't exist
    mkdir -p ./backups
    
    # Check if container is running
    if ! docker ps | grep -q $DB_CONTAINER; then
        echo "Database container is not running. Starting containers..."
        sudo docker compose up -d db
        sleep 10
    fi
    
    # Data only backup
    sudo docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME -a -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql
    
    # Full backup (schema + data)
    sudo docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}.sql
    
    # Clean backup (with drop statements)
    sudo docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME -c -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_clean.sql
    
    echo "Backups saved:"
    echo "  - Data only: ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql"
    echo "  - Full: ./backups/${PROJECT_NAME}_backup_${USER_DATE}.sql"
    echo "  - Clean: ./backups/${PROJECT_NAME}_backup_${USER_DATE}_clean.sql"
fi

# Local backup database (without Docker)
if [ "$BACKUP_local" = true ]; then
    echo "Taking local database backup: $USER_DATE"
    
    mkdir -p ./backups
    
    # Data only backup
    pg_dump $DB_NAME -a -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql
    
    # Full backup
    pg_dump $DB_NAME -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}.sql
    
    # Clean backup
    pg_dump $DB_NAME -c -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_clean.sql
    
    echo "Local backup completed"
fi

# Soft rebuild containers (preserves database)
if [ "$SOFT_REBUILD" = true ]; then
    echo "Starting soft rebuild..."
    
    # Git pull to update codebase
    echo "Pulling latest changes from git..."
    git pull
    
    echo "Stopping web and nginx containers (preserving database)"
    sudo docker compose stop web nginx cloudflared 2>/dev/null || true
    sudo docker compose rm -f web nginx cloudflared 2>/dev/null || true
    
    # Remove static volume to ensure fresh files
    echo "Removing static volume for fresh files..."
    sudo docker volume rm ${PROJECT_NAME}_static_volume 2>/dev/null || true
    sudo docker volume rm ${PROJECT_NAME}_media_volume 2>/dev/null || true
    
    # Rebuild images
    echo "Rebuilding images..."
    sudo docker compose build --no-cache web
    
    # Start containers
    echo "Starting containers"
    sudo docker compose up -d
    
    # Wait for containers to be ready
    echo "Waiting for containers to be ready..."
    sleep 15
fi

# Full rebuild containers
if [ "$REBUILD" = true ]; then
    echo "Starting full rebuild..."
    
    # Git pull to update codebase
    echo "Pulling latest changes from git..."
    git pull
    
    echo "Stopping and removing all containers"
    sudo docker compose down
    
    # Remove volumes for fresh start
    echo "Removing volumes for fresh start..."
    sudo docker volume rm ${PROJECT_NAME}_static_volume 2>/dev/null || true
    sudo docker volume rm ${PROJECT_NAME}_postgres_data 2>/dev/null || true
    sudo docker volume rm ${PROJECT_NAME}_media_volume 2>/dev/null || true
    
    # Prune images
    sudo docker image prune -f
    
    # Rebuild and start containers
    echo "Rebuilding and starting containers..."
    sudo docker compose build --no-cache
    sudo docker compose up -d
    
    # Wait for database to be ready
    echo "Waiting for containers to be ready..."
    sleep 20
fi

# Run migrations
if [ "$MIGRATE" = true ]; then
    echo "Running Django migrations"
    
    # Wait for database
    echo "Waiting for database to be ready..."
    sleep 5
    
    # Collect static files
    sudo docker compose exec web python manage.py collectstatic --noinput
    
    # Make migrations
    echo "Making migrations..."
    sudo docker compose exec web python manage.py makemigrations
    sudo docker compose exec web python manage.py makemigrations timetrack
    
    # Apply migrations
    echo "Applying migrations..."
    sudo docker compose exec web python manage.py migrate
    
    echo "Migrations completed"
fi

# Restore database
if [ "$RESTORE" = true ]; then
    echo "Restoring database from backup"
    
    if [ ! -f "./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql" ]; then
        echo "Error: Backup file not found: ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql"
        exit 1
    fi
    
    # Wait for database to be ready
    echo "Waiting for database to be ready..."
    sleep 10
    
    # Restore database
    echo "Restoring from: ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql"
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < ./backups/${PROJECT_NAME}_backup_${USER_DATE}_data.sql
    
    echo "Database restore completed"
fi

# Initial setup
if [ "$SETUP" = true ]; then
    echo "Running initial setup..."
    
    # Wait for containers to be ready
    echo "Waiting for containers to be ready..."
    sleep 10
    
    # Run migrations first
    echo "Running migrations..."
    sudo docker compose exec web python manage.py makemigrations
    sudo docker compose exec web python manage.py makemigrations timetrack
    sudo docker compose exec web python manage.py migrate
    
    # Collect static files
    sudo docker compose exec web python manage.py collectstatic --noinput
    
    # Create superuser
    echo "Creating superuser..."
    sudo docker compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@timetracker.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    
    # Create hour limits
    echo "Creating hour limits..."
    sudo docker compose exec web python manage.py shell -c "
from timetrack.models import HourLimit
if not HourLimit.objects.filter(period='weekly').exists():
    HourLimit.objects.create(period='weekly', max_hours=40)
    print('Weekly hour limit created: 40 hours')
else:
    print('Weekly hour limit already exists')

if not HourLimit.objects.filter(period='monthly').exists():
    HourLimit.objects.create(period='monthly', max_hours=160)
    print('Monthly hour limit created: 160 hours')
else:
    print('Monthly hour limit already exists')
"
    
    echo "Initial setup completed!"
    echo "You can login with: admin/admin123"
    echo "Don't forget to:"
    echo "1. Change the admin password"
    echo "2. Set up pay rates for users in /admin/"
    echo "3. Update hour limits if needed"
fi

# Deploy to production
if [ "$DEPLOY" = true ]; then
    echo "Deploying to production..."
    
    # Check if .env file has production settings
    if grep -q "DEBUG=True" .env; then
        echo "Warning: DEBUG=True found in .env file"
        echo "Make sure to set DEBUG=False for production"
    fi
    
    # Pull latest changes
    git pull
    
    # Backup before deployment
    if docker ps | grep -q $DB_CONTAINER; then
        echo "Creating backup before deployment..."
        mkdir -p ./backups
        docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME -a -O > ./backups/${PROJECT_NAME}_backup_${USER_DATE}_predeploy.sql
        echo "Pre-deployment backup saved"
    fi
    
    # Deploy
    echo "Building and starting containers..."
    sudo docker compose build --no-cache
    sudo docker compose up -d
    
    # Wait and run migrations
    echo "Waiting for containers and running migrations..."
    sleep 20
    sudo docker compose exec web python manage.py migrate
    sudo docker compose exec web python manage.py collectstatic --noinput
    
    echo "Production deployment completed!"
fi

echo "TimeTracker build script completed successfully!"

# Show container status
echo ""
echo "Container Status:"
sudo docker compose ps