# NG_CP_Team_5331
 Krishimitra - Agricultural Advisory Platform

Krishimitra is a web-based application built with Django and SQLite that helps farmers and agricultural enthusiasts manage crop records, access crop recommendations, weather forecasts, and soil analysis information.

## Features

### User Features
- User Authentication: Secure login, signup, and password recovery system.
- Dashboard: Overview of user activities and quick access to features.
- Crop Records Management: Add, view, and delete crop records including crop name, field area, sowing date, and harvest expectations.
- Crop Recommendations: Get advice on suitable crops based on various factors.
- Weather Information: Access weather forecasts to plan farming activities.
- Soil Analysis: Receive soil recommendations for better crop yield.

### Admin Features
- Admin Panel: Comprehensive Django admin interface to manage users, crop data, and system settings.
- User Oversight: View and manage all registered users and their activities.
- Data Management: Add, update, or remove crop, weather, and soil information.

## Technical Stack
- Backend: Python (Django)
- Database: SQLite
- Frontend: HTML (Django Templates), CSS, JavaScript
- Security: Django's built-in authentication and security features

## Database Schema
The system uses `db.sqlite3` with the following key tables:

- users: Authentication and profile details (Django's built-in User model).
- accounts_croprecord: Crop records containing user references, crop names, field areas, sowing dates, harvest dates, and notes.

 Project Folder Structure

KRISHIMITRA/
│
├── db.sqlite3
├── manage.py
├── requirements.txt
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── __pycache__/
│   └── migrations/
│       ├── __init__.py
│       ├── 0001_initial.py
│       └── __pycache__/
├── Krishimitra/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __pycache__/
├── static/
│   ├── css/
│   │   ├── dashboard.css
│   │   ├── form.css
│   │   └── login.css
│   └── images/
│   └── js/
│       ├── crop.js
│       ├── dashboard.js
│       ├── language.js
│       ├── location.js
│       ├── soil.js
│       └── weather.js
└── templates/
    ├── crop_records.html
    ├── crop.html
    ├── dashboard.html
    ├── forgot_password.html
    ├── login.html
    ├── signup.html
    ├── soil.html
    └── weather.html


## Getting Started

# Prerequisites
- Python 3.x
- Pip
 # Installation
1. Install the required dependencies:
   pip install -r requirements.txt
2. Run database migrations:
   python manage.py migrate
3. Run the application:
   python manage.py runserver
4. Access the application:
   Open your browser and go to `http://127.0.0.1:8000`.
