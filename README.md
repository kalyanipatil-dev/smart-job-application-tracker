# Smart Job Application Tracker

A Python-based job application tracking and analytics dashboard.

## Features

- User Signup and Login
- Job Application Management
- Search
- Filters
- Sorting
- Analytics Dashboard
- CSV Export
- Excel Export
- Word Export
- PDF Export
- Admin Dashboard
- User Management
- Activity Logs

## Admin Access

The application uses a predefined Admin account.

### Admin Credentials

Username:
`Kat`

Password:
`Kat@2026`

The Admin account is automatically created in the database when the application starts.

Admin Signup and Admin First-Time Login are not available.

The Home page contains the Admin button. Clicking it opens the Admin Login directly.

After successful Admin authentication, the Admin Dashboard provides:

- User Management
- User Status Management
- Activity Logs

## Security

The Admin password is stored in the SQLite database as a PBKDF2-SHA256 hash.

The normal Create Account form creates only regular user accounts.

Keep the GitHub repository private because the predefined Admin credentials are configured in `database.py`.
