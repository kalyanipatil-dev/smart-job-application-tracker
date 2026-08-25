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

The application uses one predefined administrator account.

### Admin Login

Username:

`Kat`

Password:

`Kat@2026`

The Admin account is automatically created when the application initializes the database.

There is:

- No Admin Signup
- No Admin First-Time Login
- No Admin OTP setup
- No Admin password creation page

The Home page contains the small **Admin** button. Clicking it opens the **Admin Login** screen directly.

After successful authentication, the Admin Dashboard provides:

- User management
- User status updates
- Activity Logs

## Security

The Admin password is converted to a PBKDF2-SHA256 password hash before being stored in the SQLite database.

The normal User Signup form always creates accounts with the `user` role.

Admin accounts cannot be created through the normal User Signup page.

**Important:** Keep this repository private because the predefined Admin credentials are configured in `database.py`.
