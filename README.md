# E-Ambulance

A Django-based web application for requesting and dispatching ambulances with real-time chat between users and administrators.

## Tech Stack
- **Backend Framework:** Django 5.2.5 (WSGI/ASGI)
- **Real-time:** Django Channels 4.3.1 with InMemoryChannelLayer
- **ASGI Server:** Daphne 4.2.1
- **Database (dev):** SQLite via Django ORM (`db.sqlite3`)
- **Templating:** Django Templates (`APP_DIRS=True`)
- **UI / CSS:** Bootstrap 5.3 (CDN) + custom inline CSS branding (see `ambulance/templates/home.html`)
- **Forms:** django-widget-tweaks 1.5.0
- **Auth & Sessions:** Session-based login storing `user_id` with custom `User` model in `ambulance.models`
- **Email:** SMTP (Gmail) config in settings for outgoing mail

## Key Files & Directories
- **Project settings:** `E_ambulance/settings.py`
- **ASGI/WSGI apps:** `E_ambulance/asgi.py`, `E_ambulance/wsgi.py`
- **App (domain logic):** `ambulance/` (models, views, forms, consumers, templates)
- **Templates:** `ambulance/templates/` (e.g., `home.html`, `chat_list.html`, `chat_user.html`)
- **Database:** `db.sqlite3`
- **Dependencies:** `requirements.txt`

## Real-time Chat
- **Channels config:** `ASGI_APPLICATION = "E_ambulance.asgi.application"`, `CHANNEL_LAYERS` uses `InMemoryChannelLayer` (dev only)
- **Consumers:** `ambulance/consumers.py`
- **Views:** `user_chat_view`, `admin_chat_view`, `user_chat_list` in `ambulance/views.py`

For production, consider Redis channel layer (`channels_redis`) and a persistent ASGI server setup.

## Local Development
1. **Create & activate venv**
   - Windows: `python -m venv venv && venv\Scripts\activate`
2. **Install dependencies**
   - `pip install -r requirements.txt`
3. **Run migrations**
   - `python manage.py migrate`
4. **Start server (dev)**
   - Django dev: `python manage.py runserver`
   - Daphne (ASGI): `daphne E_ambulance.asgi:application`

## Security Notes
- Move secret keys and email credentials out of `E_ambulance/settings.py` into environment variables for safety.
- Replace `InMemoryChannelLayer` with Redis for production deployments.
