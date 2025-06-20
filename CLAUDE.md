# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based coworking space reservation system that allows users to register, get approved by administrators, and make reservations through a web interface with calendar functionality.

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite3 with manual SQL queries
- **Frontend**: Bootstrap 5, FullCalendar.js
- **Authentication**: Session-based with password hashing (SHA256)
- **Email**: SMTP integration for notifications

## Development Commands

### Running the Application
```bash
python app.py
```
The app runs on `http://localhost:5000` by default.

### Windows Server Deployment
```bash
run_server.bat
```

### Required Dependencies
```bash
pip install flask
```

## Architecture

### Database Schema
- **users**: id, name, email, password_hash, is_approved, is_admin, created_at
- **reservations**: id, user_id, date, start_time, end_time, purpose, created_at

### Key Components
- `app.py`: Main Flask application with all routes and business logic
- `utils.py`: Database initialization, email sending, validation functions
- `config.json`: SMTP settings, business rules, application settings
- Templates use Jinja2 with Bootstrap for responsive design
- FullCalendar.js for interactive calendar functionality

### Authentication Flow
1. Users register and wait for admin approval
2. Admin manually approves users through admin interface
3. Approved users can login and make reservations
4. Default admin account: admin@example.com / admin123

### Business Rules
- Operating hours: 9:00-18:00, Monday-Saturday
- Minimum booking: 1 hour, Maximum: 8 hours per day
- Advance booking: Up to 30 days
- Email notifications for registrations and reservations

## File Structure

```
/
├── app.py              # Main Flask application
├── utils.py           # Helper functions (DB, email, validation)
├── config.json        # Configuration settings
├── templates/         # Jinja2 HTML templates
├── static/           # CSS and JavaScript files
└── coworking.db      # SQLite database (auto-created)
```

## Common Development Tasks

### Adding New Routes
Add route handlers in `app.py` following the existing pattern with decorators for authentication (`@login_required`, `@admin_required`).

### Database Changes
Modify `init_database()` in `utils.py` for schema changes. The database is auto-created on first run.

### Frontend Changes
- Templates are in `templates/` directory using Bootstrap 5
- Static files in `static/` directory
- Calendar functionality in `static/calendar.js`

### Configuration Updates
Modify `config.json` for email settings, business rules, or application settings.

## Security Considerations

- Password hashing uses SHA256 (consider upgrading to bcrypt for production)
- Session-based authentication with secret key
- SQL injection prevention through parameterized queries
- SMTP credentials stored in config.json (should be environment variables in production)