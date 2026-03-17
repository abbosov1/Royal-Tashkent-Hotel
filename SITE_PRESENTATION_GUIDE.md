# Royal Tashkent Hotel - Presentation Guide

## 1. Project Overview
Royal Tashkent Hotel is a full-stack hotel booking web application with three user levels:
- Guest: can browse rooms and site content
- Registered user: can book, reschedule, and cancel reservations
- Admin: can manage rooms, bookings, and users

The app uses a server-rendered architecture with FastAPI + Jinja2 and SQLAlchemy for data persistence.

## 2. Tech Stack
- Backend framework: FastAPI
- Template engine: Jinja2
- ORM: SQLAlchemy
- Database: PostgreSQL (configured via `DATABASE_URL`)
- Authentication: JWT in `HttpOnly` cookie + bcrypt hashing
- Frontend: HTML, CSS, JavaScript
- Deployment/runtime: Docker + docker-compose

Main code files:
- `app/main.py` - routes and business logic
- `app/models.py` - data models (`User`, `Room`, `Booking`)
- `app/auth.py` - password hashing and JWT utilities
- `app/database.py` - DB engine/session setup
- `app/templates/*.html` - UI pages
- `app/static/css/*.css` and `app/static/js/*.js` - frontend styling and behavior

## 3. System Architecture and Flow
### 3.1 User Flow
1. User opens `/` and browses rooms.
2. If not authenticated, booking redirects to `/login`.
3. After login, booking creates a record in `bookings`.
4. In `/dashboard`, user can:
- view their bookings
- reschedule booking dates
- cancel bookings

### 3.2 Admin Flow
1. Admin opens `/admin`.
2. Admin can:
- add/edit/delete rooms
- delete bookings
- delete non-admin users
- update admin account settings

### 3.3 Authentication and Session Handling
- On successful login, a JWT is created with `sub = user email`.
- Token is stored in `access_token` (`HttpOnly` cookie).
- Current user is resolved from cookie in `get_current_user_from_cookie`.
- Protected routes enforce role checks for admin-only actions.

## 4. Data Model
### `users`
- `id`
- `full_name`
- `email` (unique)
- `hashed_password`
- `is_active`
- `is_admin`

### `rooms`
- `id`
- `name`
- `description`
- `price_per_night`
- `image_url`

### `bookings`
- `id`
- `user_id` -> `users.id`
- `room_id` -> `rooms.id`
- `check_in_date`
- `check_out_date`
- `total_price`
- `created_at`

## 5. Core Features
- User registration and login
- JWT cookie-based session management
- Room booking with automatic total price calculation
- User dashboard for booking management
- Admin panel for full operational control
- Multilingual UI: English, Russian, Uzbek
- SEO landing page: `/hotel-in-tashkent`
- Responsive interface for desktop and mobile

## 6. Internationalization (i18n)
Localization is centralized in `app/static/js/i18n.js`:
- All translatable values are stored in the `I18N` dictionary
- UI nodes use `data-i18n` keys
- Selected language is persisted in `localStorage`
- Language switch updates content at runtime across pages

## 7. Image Upload Strategy (important for Vercel/readonly FS)
For admin room uploads, images are converted to Base64 data URLs (within size limits) and stored in DB-linked fields. This avoids dependence on writable local filesystem in serverless/readonly environments.

## 8. Route Map
Public routes:
- `GET /`
- `GET /hotel-in-tashkent`
- `GET /login`, `POST /login`
- `GET /register`, `POST /register`
- `GET /logout`

User routes:
- `POST /book/{room_id}`
- `GET /dashboard`
- `POST /dashboard/booking/cancel/{booking_id}`
- `POST /dashboard/booking/reschedule/{booking_id}`

Admin routes:
- `GET /admin`
- `POST /admin/room/add`
- `POST /admin/room/edit/{room_id}`
- `POST /admin/room/delete/{room_id}`
- `POST /admin/booking/delete/{booking_id}`
- `POST /admin/user/delete/{user_id}`
- `POST /admin/settings`

## 9. Security Notes
Implemented:
- Password hashing via bcrypt
- JWT stored in `HttpOnly` cookie
- Access control checks for user and admin routes

Recommended future hardening:
- CSRF protection for form endpoints
- Login rate limiting
- Strict cookie flags in production (`secure`, `samesite`)
- Stronger input validation and sanitization

## 10. How to Run
### Docker
Run:
```bash
docker-compose up -d --build
```

### Local (without Docker)
1. Install dependencies from `requirements.txt`
2. Set `DATABASE_URL`
3. Run FastAPI app with `uvicorn`

## 11. Recommended Demo Script (for presentation)
1. Open homepage: show design, room cards, filters, language switching.
2. Register a new user account.
3. Log in and create a booking.
4. Open dashboard and reschedule/cancel booking.
5. Log in as admin and manage rooms/bookings.
6. Show multilingual content and SEO page `/hotel-in-tashkent`.

## 12. 30-Second Pitch
"Royal Tashkent Hotel is a production-style booking platform built with FastAPI. It supports full user booking flows, role-based admin operations, multilingual content, and responsive design. Authentication is implemented with JWT cookies, data is managed through SQLAlchemy, and the app is containerized with Docker for reliable deployment."

## 13. Quick Q&A Preparation
Q: Why FastAPI?
A: High performance, clean routing, easy dependency injection, and strong ecosystem for API/web backends.

Q: How do you separate roles?
A: User identity comes from JWT cookie; admin routes enforce `is_admin` or configured admin email checks.

Q: How is booking price calculated?
A: `total_price = number_of_days * room.price_per_night`; minimum stay cost is enforced as at least one day.

Q: How is multilingual support implemented?
A: Dictionary-driven translation map in `i18n.js` with `data-i18n` keys across templates.

Q: What is the main deployment challenge solved?
A: File upload handling in readonly/serverless environments using Base64 image storage strategy.