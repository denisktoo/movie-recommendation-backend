# 🎬 Movie Recommendation Backend API

A RESTful Movie Recommendation API built with **Django REST Framework**, featuring:

* **JWT authentication**
* **Role-based access (User, Admin)**
* **TMDB integration for trending movies**
* **Personalized recommendations (search history & ratings-based)**
* **Favorites, Watchlist & Ratings management**
* **Search history tracking with clear functionality**
* **Recommendation caching per user**
* **Search & filtering with pagination**
* **Async email notifications with Celery**
* **Swagger API documentation**
* **Dockerized setup with Postgres and Redis**

---

## ⚙️ Setup (local)

You can run the entire stack — including **PostgreSQL**, **Redis**, and **Celery** — using Docker.

### 🐳 Using Docker Compose

```bash
docker compose up -d --build
```

This command:

* Builds your Docker images (based on your `Dockerfile`)
* Starts containers for:

  * PostgreSQL (Database)
  * Redis (Celery broker & result backend)
  * Django (web app)
  * Celery worker

Once everything is running:

* Django: `http://localhost:8000`
* Swagger Docs: `http://localhost:8000/api/docs/`
* PostgreSQL and Redis connect automatically via Docker network aliases.

### 🚀 Running After the Initial Build

After the initial build, use the simpler command for subsequent startups:

```bash
docker compose up -d
```

If you make changes to your application code:

```bash
docker compose up -d --build
```

Quick operational commands:

```bash
# check running services
docker compose ps

# see web logs
docker compose logs -f web

# see celery logs
docker compose logs -f celery

# stop services (keep containers)
docker compose stop

# remove containers/network
docker compose down
```

### 🧩 Local Manual Setup (without Docker)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Run Celery Worker (process tasks)

```bash
celery -A movie_recommendation_backend worker -l info
```

The API will be available at `http://127.0.0.1:8000/`

---

## 🧰 Redis & Celery Configuration

The project integrates **Celery** and **Redis** through the following configuration:

* **Celery Broker:** Redis (`redis://redis:6379/0`)
* **Celery Result Backend:** Redis (`redis://redis:6379/0`)
* **Serialization:** JSON for both tasks and results

This setup ensures async email tasks are queued and processed without blocking API responses.

> **Docker vs local note:** Inside Docker, use `redis://redis:6379/0` (service name). Running Celery locally outside Docker, use `redis://127.0.0.1:6379/0` (host machine). Using the wrong address is the most common reason Celery fails to connect.

---

## 🔑 TMDB API Configuration

This project integrates with **[The Movie Database (TMDB) API](https://www.themoviedb.org/)** to fetch trending and recommended movie data.

Add your TMDB API key to your `.env` file:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

> Get your API key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) — it's free.

---

## 🔐 Authentication

### Register User

**POST** `/api/register/`
Request example:

```json
{
  "username": "kip",
  "email": "kip@example.com",
  "password": "kip*#123"
}
```

Response:

```json
{
  "detail": "Your account has been created successfully.",
  "user": {
    "id": 1,
    "username": "kip",
    "email": "kip@example.com",
    "role": "user"
  }
}
```

> Notes: `role` defaults to `user`. It cannot be set at registration — admin role is assigned internally only. A welcome email is sent asynchronously via Celery after the account is created.

### Login (JWT)

**POST** `/api/token/`
Request example:

```json
{
  "username": "kip",
  "password": "kip*#123"
}
```

Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR..."
}
```

### Refresh Token

**POST** `/api/token/refresh/`
Request:

```json
{
  "refresh": "<your_refresh_token>"
}
```

All protected endpoints require the header:

```
Authorization: Bearer <access_token>
```

---

## 🏠 API Root

### API Root (`/api/`)

**GET** `/api/`
DRF API root — returns links to top-level resources:

```json
{
  "users": "http://127.0.0.1:8000/api/users/",
  "movies": "http://127.0.0.1:8000/api/movies/",
  "searches": "http://127.0.0.1:8000/api/searches/",
  "recommendations": "http://127.0.0.1:8000/api/recommendations/",
  "generated-recommendations": "http://127.0.0.1:8000/api/generated-recommendations/"
}
```

---

## 👤 User Management

* **List All Users (Admin only)** → `GET /api/users/`
* **Retrieve User (Owner/Admin)** → `GET /api/users/{id}/`
* **Update User (Owner/Admin)** → `PATCH /api/users/{id}/`
* **Delete User (Admin only)** → `DELETE /api/users/{id}/`

> Notes: Normal users can only see and edit their own account. Admin sees all users. Role cannot be changed by normal users — only admin can promote accounts.

Update example:

```json
{
  "email": "newemail@example.com"
}
```

---

## 🎬 Movies

Movies are fetched from TMDB and cached locally. The database acts as a local mirror for performance and to support favorites, watchlist, and ratings.

* **List Trending Movies (Public)** → `GET /api/movies/`
* **Retrieve Movie (Public)** → `GET /api/movies/{id}/`
* **Filter Movies** → `GET /api/movies/?release_date=2026-03-15`

> Notes: Each `GET /api/movies/` call fetches the latest trending movies from TMDB, updates the local cache, and returns a clean serialized response. Only admins can write to the movie resource directly.

Response example:

```json
[
  {
    "tmdb_id": 687163,
    "title": "Project Hail Mary",
    "poster_path": "/yihdXomYb5kTeSivtFndMy5iDmf.jpg",
    "release_date": "2026-03-15",
    "cached_at": "2026-04-14T08:00:00Z"
  }
]
```

---

## ❤️ Favorites

* **List My Favorites (Authenticated)** → `GET /api/users/{user_id}/favorites/`
* **Add Favorite (Authenticated)** → `POST /api/users/{user_id}/favorites/`
* **Remove Favorite (Owner/Admin)** → `DELETE /api/users/{user_id}/favorites/{id}/`

> Notes: `user` is always set from `request.user`. The `movie` field refers to the local Movie primary key — load movies first via `GET /api/movies/` to get valid IDs.

Add favorite example:

```json
{
  "movie": 1
}
```

---

## 📺 Watchlist

* **List My Watchlist (Authenticated)** → `GET /api/users/{user_id}/watchlist/`
* **Add to Watchlist (Authenticated)** → `POST /api/users/{user_id}/watchlist/`
* **Remove from Watchlist (Owner/Admin)** → `DELETE /api/users/{user_id}/watchlist/{id}/`

Add to watchlist example:

```json
{
  "movie": 3
}
```

---

## ⭐ Ratings

* **List My Ratings (Authenticated)** → `GET /api/users/{user_id}/ratings/`
* **Rate a Movie (Authenticated)** → `POST /api/users/{user_id}/ratings/`
* **Update Rating (Owner/Admin)** → `PATCH /api/users/{user_id}/ratings/{id}/`
* **Delete Rating (Owner/Admin)** → `DELETE /api/users/{user_id}/ratings/{id}/`

> Notes: Rating must be between 0 and 5. Each user can only rate a movie once — update the existing rating if you want to change it.

Rate a movie example:

```json
{
  "movie": 1,
  "rating": 4.5
}
```

Update rating example:

```json
{
  "rating": 5
}
```

---

## 🔍 Search History

Search history is a log of what the user has searched for. It feeds into the recommendation engine.

* **List My Search History (Authenticated)** → `GET /api/searches/`
* **Add Search Entry (Authenticated)** → `POST /api/searches/`
* **Delete One Entry (Owner)** → `DELETE /api/searches/{id}/`
* **Clear All History (Owner)** → `DELETE /api/searches/clear/`

Add search entry example:

```json
{
  "query": "space adventure"
}
```

Response:

```json
{
  "id": 4,
  "query": "space adventure",
  "searched_at": "2026-04-14T09:22:00Z"
}
```

---

## 🧠 Recommendations

Two recommendation strategies are supported — both use the user's own behavior to personalize results.

### From Search History

**GET** `/api/generated-recommendations/from-search-history/`

*What it does:*
Reads the user's recent search queries, extracts keywords, searches TMDB using those terms, saves results locally, excludes movies already rated/favorited/watchlisted, caches the result, and returns a ranked movie list.

> Best when the user has active search history. Returns up to 10 movies.

Response example:

```json
[
  {
    "tmdb_id": 687163,
    "title": "Project Hail Mary",
    "poster_path": "/yihdXomYb5kTeSivtFndMy5iDmf.jpg",
    "release_date": "2026-03-15",
    "cached_at": "2026-04-14T08:00:00Z"
  }
]
```

If no search history exists:

```json
{
  "detail": "No recommendations were found from your recent searches yet. Try searching for a few movies or genres first.",
  "results": []
}
```

### From Ratings

**GET** `/api/generated-recommendations/from-ratings/`

*What it does:*
Reads movies the user rated 4 or above, fetches TMDB recommendations based on each liked movie, merges and ranks results by frequency of appearance, excludes already interacted movies, caches the result, and returns a ranked movie list.

> Best when the user has rated several movies. More stable and accurate than search-based recommendations.

If no qualifying ratings exist:

```json
{
  "detail": "No recommendations were found from your ratings yet. Rate a few movies first to get personalized suggestions.",
  "results": []
}
```

---

## 📦 Recommendation Cache

After recommendations are generated, results are stored per user per type for fast reuse.

* **List My Cached Recommendations (Authenticated)** → `GET /api/recommendations/`
* **Retrieve One Cache Entry** → `GET /api/recommendations/{id}/`

Response example:

```json
[
  {
    "id": 1,
    "cache_type": "search_history",
    "data": {
      "count": 10,
      "results": [...]
    },
    "updated_at": "2026-04-14T09:30:00Z"
  },
  {
    "id": 2,
    "cache_type": "ratings",
    "data": {
      "count": 8,
      "results": [...]
    },
    "updated_at": "2026-04-14T09:35:00Z"
  }
]
```

> Notes: Cache is system-managed. It updates automatically each time a recommendation endpoint is called. Users cannot create or delete cache entries directly.

---

## 🔎 Available Query Params

| Endpoint | Query Params | Example |
| --- | --- | --- |
| `/api/users/` | `username`, `email`, `role` | `/api/users/?role=admin` |
| `/api/movies/` | `release_date` | `/api/movies/?release_date=2026-03-15` |
| `/api/searches/` | — | — |
| `/api/users/{id}/favorites/` | — | — |
| `/api/users/{id}/watchlist/` | — | — |
| `/api/users/{id}/ratings/` | — | — |
| `/api/recommendations/` | — | — |

---

## 🔐 Role-Based Access Control

| Role | Permissions |
| --- | --- |
| **User** | Manage own favorites, watchlist, ratings, search history, view movies, get recommendations |
| **Admin** | Full access: manage users, movies, and all user-owned resources |

> Role escalation is blocked at every layer — serializer, view, and model. Only an admin can promote another user's role.

---

## 📊 Response Format

Example paginated response:

```json
{
  "count": 20,
  "total_pages": 2,
  "current_page": 1,
  "next": "http://127.0.0.1:8000/api/movies/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 🔧 Features & Background Tasks

### ✅ Celery (Async Emails)

* Sends a welcome email asynchronously after user registration
* Uses **Redis** as both the message broker and result backend
* Email task is triggered via `transaction.on_commit()` — ensures the user is fully committed to the database before the worker attempts to read it

### ✅ Redis

* Serves dual roles:

  * **Celery broker** — receives and queues tasks from Django
  * **Celery result backend** — stores task execution results
* Runs in its own Docker container and connects via `redis://redis:6379`

---

## 🚀 Recommended Workflow

1. Start containers:

```bash
docker compose up --build -d
```

2. Register a user → `POST /api/register/`  *(welcome email sent automatically via Celery)*
3. Login → `POST /api/token/` → copy your `access` token
4. Load trending movies → `GET /api/movies/`
5. Add favorites, rate movies, log searches
6. Hit recommendation endpoints to get personalized results
7. Check `GET /api/recommendations/` to see cached recommendation data
8. 🧪 Check Celery logs for background task execution:

* Stream logs (live)

```bash
docker compose logs -f celery
```

* View logs (static)

```bash
docker compose logs celery
```

---

## 📖 API Documentation

Swagger UI is available at:

```
http://127.0.0.1:8000/api/docs/
```

<!-- ReDoc is available at:

```
http://127.0.0.1:8000/api/redoc/
``` -->

> If Swagger UI looks broken (missing CSS/JS), ensure `drf_yasg` is in `INSTALLED_APPS` and run `python manage.py collectstatic`.

---

## 🔧 Environment Variables

Create a `.env` file at the project root:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

DB_NAME=movie_recommendation_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432

TMDB_API_KEY=your_tmdb_api_key

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

> `DB_HOST` should be `db` when running with Docker Compose, or `localhost` for local manual setup. Redis broker and backend URLs are set automatically per environment — `redis://redis:6379/0` inside Docker, `redis://127.0.0.1:6379/0` when running locally outside Docker.