# TimeTracker =P

A modern, mobile-first Progressive Web App (PWA) for time tracking with Django, PostgreSQL, and Docker. Features user authentication, pay calculation, hour limits, and admin dashboard.

## Features

### For Users
- � Simple clock in/out functionality
- =� Mobile-first responsive design
- =� Weekly and monthly time tracking
- =� Time entry descriptions
-  Edit and delete time entries
- = Secure user authentication

### For Administrators
- =� Admin dashboard with statistics
- =� Pay calculation and reporting
- � Hour limit monitoring with progress bars
- =e User management and statistics
- =� Detailed pay reports with date ranges
- =� Real-time tracking of active users

### Technical Features
- =� Progressive Web App (PWA)
- =3 Docker containerization
- =� Cloudflare deployment ready
- =� PostgreSQL database
- = Security best practices
- =� Bootstrap UI framework

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker (for containerized deployment)

### Local Development

1. **Clone and setup:**
```bash
git clone <repo-url>
cd TimeTracker
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. **Environment setup:**
```bash
cp .env.example .env
# Edit .env with your database settings
```

3. **Database setup:**
```bash
python manage.py migrate
python setup.py  # Creates initial data
python manage.py createsuperuser
```

4. **Run development server:**
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

### Docker Deployment

1. **Quick start with Docker Compose:**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python setup.py
docker-compose exec web python manage.py createsuperuser
```

2. **Access the application:**
- Frontend: http://localhost
- Admin: http://localhost/admin

## Project Structure

```
TimeTracker/
   timetracker/          # Django project settings
   timetrack/            # Main Django app
      models.py         # Database models
      views.py          # User views
      admin_views.py    # Admin dashboard views
      forms.py          # Django forms
      admin.py          # Django admin configuration
      urls.py           # URL routing
   templates/            # HTML templates
      base.html         # Base template with PWA features
      timetrack/        # App-specific templates
   static/               # Static files
      manifest.json     # PWA manifest
      sw.js            # Service worker
   docker-compose.yml    # Docker services
   Dockerfile           # Django container
   nginx.conf           # Nginx configuration
   requirements.txt     # Python dependencies
```

## Database Models

### TimeEntry
- User association
- Clock in/out timestamps
- Description (optional)
- Automatic duration calculation

### PayRate
- User-specific hourly rates
- Admin configurable

### HourLimit
- Weekly/monthly hour limits
- System-wide configuration

## API Endpoints

### User Routes
- `/` - Dashboard
- `/login/` - User login
- `/register/` - User registration
- `/clock-in/` - Clock in form
- `/clock-out/<id>/` - Clock out confirmation
- `/time-entry/create/` - Manual time entry
- `/time-entry/<id>/edit/` - Edit time entry

### Admin Routes
- `/admin-dashboard/` - Admin overview
- `/pay-report/` - Detailed pay reports
- `/admin/` - Django admin panel

## Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=timetracker
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432
```

### Admin Setup
1. Create superuser: `python manage.py createsuperuser`
2. Access admin panel: `/admin/`
3. Configure pay rates for users
4. Set hour limits (weekly/monthly)

## PWA Features

The application includes full PWA support:
- **Manifest**: App-like installation on mobile devices
- **Service Worker**: Offline functionality and caching
- **Responsive Design**: Mobile-first UI
- **Touch-friendly**: Large buttons and easy navigation

## Deployment

### Cloudflare Deployment
See [cloudflare-deployment.md](cloudflare-deployment.md) for detailed deployment instructions.

### Production Considerations
- Use environment variables for sensitive settings
- Configure proper SSL certificates
- Set up database backups
- Monitor application logs
- Configure Cloudflare security settings

## Security Features

- CSRF protection
- XSS protection
- Secure headers (HSTS, X-Frame-Options)
- User authentication required
- Admin-only access to sensitive data
- SQL injection protection via Django ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section in [cloudflare-deployment.md](cloudflare-deployment.md)
2. Review the application logs
3. Create an issue in the repository

## Changelog

### v1.0.0
- Initial release
- User authentication system
- Time tracking with clock in/out
- Admin dashboard with pay calculation
- PWA support
- Docker deployment
- Cloudflare configuration