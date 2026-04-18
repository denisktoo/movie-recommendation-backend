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
* **CI/CD with GitHub Actions and Jenkins**

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

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

> `DB_HOST` should be `db` when running with Docker Compose, or `localhost` for local manual setup. Redis broker and backend URLs are set automatically per environment — `redis://redis:6379/0` inside Docker, `redis://127.0.0.1:6379/0` when running locally outside Docker.

---

## ⚙️ CI/CD & Deployment

This project uses **GitHub Actions** for CI/CD and **Jenkins** (via Docker) for local pipeline automation.

* `.github/workflows/ci.yml` runs tests and linting on every push and pull request.
* `.github/workflows/dep.yml` builds and pushes the Docker image to Docker Hub on every push to `main`.
* `Jenkinsfile` defines a full pipeline: checkout → setup → test → Docker build → Docker push.
* `jenkins/Dockerfile` extends the official Jenkins LTS image with Docker pre-installed, so pipelines can build images without installing it on every run.
* `pytest.ini` configures pytest discovery so Jenkins can locate Django tests correctly.

**Local Development:** uses **Docker Compose** for the full app stack, with Jenkins added as a service.
**CI (GitHub Actions):** spins up PostgreSQL and Redis as service containers and runs Django tests in a clean environment.
**CD (GitHub Actions):** builds and tags the Docker image with both `latest` and the short Git commit SHA, then pushes to Docker Hub.
**Jenkins:** runs tests using `pytest` with JUnit XML report generation for dashboard-level test visibility. Uses SQLite in place of PostgreSQL during tests so no database sidecar is required inside the pipeline container.

**Secrets**: `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD` are stored in GitHub Secrets for the CD workflow. `DJANGO_SECRET_KEY`, `TMDB_API_KEY`, and `EMAIL_HOST_PASSWORD` are stored as GitHub Secrets for CI and as **Secret text** credentials in Jenkins — never hardcoded in either pipeline file.

---

## 🧪 GitHub Actions Workflows

### CI — `.github/workflows/ci.yml`

Triggered on every push and pull request to `main`. Runs against a live PostgreSQL service container on `127.0.0.1:5432`.

What it does:
* Installs system dependencies (`gcc`, `libpq-dev`)
* Installs Python dependencies from `requirements.txt`
* Runs `python manage.py migrate`
* Runs `flake8 .` — fails the build on any lint error
* Runs `coverage run manage.py test` and generates `coverage.xml`
* Uploads `coverage.xml` as a build artifact

> Linting respects `.flake8` config at the project root — migrations and virtual environments are excluded automatically.

### CD — `.github/workflows/dep.yml`

Triggered on every push to `main`. Builds and pushes the Docker image to Docker Hub.

What it does:
* Logs into Docker Hub using `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD` secrets
* Builds the image and tags it with both `latest` and the short Git commit SHA
* Pushes both tags to Docker Hub: `kiprotich507/movie-recommendation-backend`

---

## 🏗️ Jenkins Pipeline

Jenkins runs as a service inside Docker Compose alongside the app stack. The `Jenkinsfile` at the project root defines the full pipeline.

### Running Jenkins

Jenkins starts automatically with the rest of the stack:

```bash
docker compose up -d --build
```

Access the Jenkins dashboard at:

```
http://localhost:8080
```

Get the initial admin password:

```bash
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Required Jenkins Plugins

Install these from **Manage Jenkins → Plugins**:

* Git
* Pipeline
* JUnit
* Credentials Binding
* Workspace Cleanup
* Docker Pipeline

### Required Jenkins Credentials

Add these from **Manage Jenkins → Credentials → Global**:

| Credential ID | Kind | Used for |
| --- | --- | --- |
| `github-credentials` | Username with password | Git checkout |
| `docker-credentials` | Username with password | Docker Hub push |
| `django-secret-key` | Secret text | Django `SECRET_KEY` |
| `tmdb-api-key` | Secret text | TMDB API key |
| `email-host-password` | Secret text | Gmail app password |

> For GitHub, use a **Personal Access Token** instead of a password. For Docker Hub, use an **access token** from your Docker Hub security settings. The three `Secret text` credentials store only the raw value — no username field. Storing them as `Username with password` causes Jenkins to split them into `_USR`/`_PSW` variables and raises an insecure interpolation warning.

### Creating the Pipeline Job

1. Go to **Dashboard → New Item**
2. Enter name: `movie-recommendation-backend`
3. Select **Pipeline** → click **OK**
4. Under **Pipeline**, set:
   * Definition: `Pipeline script from SCM`
   * SCM: `Git`
   * Repository URL: `https://github.com/denisktoo/movie-recommendation-backend.git`
   * Credentials: `github-credentials`
   * Branch Specifier: `*/main`
   * Script Path: `Jenkinsfile`
5. Click **Save**, then click **Build Now** to trigger manually

### Pipeline Stages

```
Checkout → Setup Python Environment → Run Tests → Get Git Commit Hash → Build Docker Image → Push Docker Image
```

* **Checkout** — pulls repo from GitHub using `github-credentials`
* **Setup Python Environment** — installs `gcc`, `libpq-dev`, `docker.io`, and all Python dependencies inside a `python:3.12` Docker agent; also installs `pytest-django` for Django-aware test discovery
* **Run Tests** — runs `pytest --junitxml=report.xml` using the SQLite override so no Postgres sidecar is needed; JUnit report is published to the Jenkins dashboard
* **Get Git Commit Hash** — assigns the short commit SHA directly to `IMAGE_TAG` for version traceability
* **Build Docker Image** — builds and tags as both `latest` and `<commit-hash>`
* **Push Docker Image** — logs into Docker Hub using single-quoted shell strings throughout to avoid Groovy string interpolation of credentials; pushes both tags using `docker-credentials`

> **Note on secure interpolation:** All `sh` blocks in the Jenkinsfile use single-quoted strings (`'''...'''`) so Groovy never interpolates sensitive variables. Shell environment variables are resolved by the shell instead, which is the Jenkins-recommended pattern.

### pytest Configuration

`pytest.ini` at the project root tells pytest where to find the Django settings module and which files to treat as test files:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = movie_recommendation_backend.settings
python_files = tests.py test_*.py *_tests.py
```

Without this file, pytest cannot discover Django tests because it does not know the settings module and does not match the `tests.py` naming convention by default. `pytest-django` must also be installed — it is listed in `requirements.txt`.

### SQLite Override for Jenkins Tests

The Jenkins pipeline runs tests inside a `python:3.12` Docker agent with no Postgres available. To avoid needing a database sidecar, `settings.py` overrides the database to SQLite when the `USE_SQLITE_FOR_TESTS` environment variable is set:

```python
import os

if os.environ.get('USE_SQLITE_FOR_TESTS'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        }
    }
```

The Jenkinsfile sets `USE_SQLITE_FOR_TESTS = 'true'` in its environment block. This means `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_HOST` are not required during Jenkins test runs. GitHub Actions CI still uses a real PostgreSQL service container and is unaffected by this override.

---

## 🔍 Code Quality

Flake8 is configured via `.flake8` at the project root:

```ini
[flake8]
max-line-length = 88
exclude =
    .git,
    __pycache__,
    env,
    venv,
    .venv,
    .pytest_cache,
    migrations
```

This ensures migrations are not linted, virtual environments are excluded, and the line length limit is consistent with Black's default of 88 characters.

Run locally:

```bash
flake8 .
```

### ✅ Dockerfile ENV Format

The app `Dockerfile` uses the current `KEY=value` format for `ENV` instructions:

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```

The legacy `ENV key value` (space-separated) format is deprecated and raises a `LegacyKeyValueFormat` warning in Docker build output. Using `=` is the correct format per current Docker best practice.

---

## 🐳 Docker Hub

The production-ready Docker image is available at:

```
kiprotich507/movie-recommendation-backend
```

Tags pushed on every successful CD run:

* `latest` — always points to the most recent build from `main`
* `<commit-sha>` — short Git commit hash for version traceability (e.g. `a1b2c3`)

Pull the image:

```bash
docker pull kiprotich507/movie-recommendation-backend:latest
```
