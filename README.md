# Find Your Worker Platform

A full-stack web platform that connects users with local service workers (plumbers, electricians, cleaners, etc.). Built with Flask and SQLite.

## Features

- User and worker registration with separate dashboards
- Browse and book services by category
- Admin dashboard for platform management
- Nearby worker discovery
- Chatbot support
- Subscription plans and loyalty rewards
- Service tracking

## Tech Stack

- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML, CSS

## How to Run

1. Clone the repository
```bash
   git clone https://github.com/shreya-User/find-your-worker-platform.git
   cd find-your-worker-platform
```
2. Install dependencies
```bash
   pip install -r requirements.txt
```
3. Run the app
```bash
   python app.py
```
4. Open `http://localhost:5000` in your browser

## Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application |
| `index.html` | Landing page |
| `user_dashboard.html` | User interface |
| `worker_dashboard.html` | Worker interface |
| `admin_dashboard.html` | Admin controls |
| `service_portal.db` | SQLite database |
