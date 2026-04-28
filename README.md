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
* **Kubernetes deployment with Minikube (local orchestration)**

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
  "username": "john",
  "email": "john@yourdomain.com",
  "password": "John*#123"
}
```

Response:

```json
{
  "detail": "Your account has been created successfully.",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@yourdomain.com",
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
  "username": "john",
  "password": "John*#123"
}
```

Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR..."
}
```

Copy the `access` token — all protected endpoints require this header:

```
Authorization: Bearer <access_token>
```

### Refresh Token

**POST** `/api/token/refresh/`

Request:

```json
{
  "refresh": "<your_refresh_token>"
}
```

### Logout

**POST** `/api/logout/`

Blacklists the refresh token so it can no longer be used to obtain new access tokens.

Request:

```json
{
  "refresh": "<your_refresh_token>"
}
```

Response:

```json
{
  "message": "Logout successful"
}
```

---

## 🏠 API Root

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
  "email": "newemail@yourdomain.com"
}
```

---

## 👤 Profile Management

* **Create Profile (Authenticated)** → `POST /api/profiles/`
* **List My Profile (Authenticated)** → `GET /api/profiles/`

> Notes: `user` is set automatically from `request.user`. Each user has one profile. Creating a profile twice will update the existing one.

Create profile example:

```json
{
  "bio": "Backend developer with a passion for Python and APIs.",
  "location": "Nairobi, Kenya"
}
```

---

## 🎬 Movies

Movies are fetched from TMDB and cached locally. The database acts as a local mirror for performance and to support favorites, watchlist, and ratings.

* **List Trending Movies (Public)** → `GET /api/movies/`
* **Retrieve Movie (Public)** → `GET /api/movies/{id}/`
* **Filter Movies** → `GET /api/movies/?release_date=2026-03-15`

> Notes: Each `GET /api/movies/` call fetches the latest trending movies from TMDB, updates the local cache, and returns a clean serialized response. Only admins can write to the movie resource directly. You must call this endpoint before using favorites, watchlist, or ratings — those resources reference local movie IDs that only exist after TMDB results are cached.

Response example:

```json
[
  {
    "id": 1,
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

* **Add Favorite (Authenticated)** → `POST /api/users/{user_id}/favorites/`
* **List My Favorites (Authenticated)** → `GET /api/users/{user_id}/favorites/`
* **Remove Favorite (Owner/Admin)** → `DELETE /api/users/{user_id}/favorites/{id}/`

> Notes: `user` is set automatically from `request.user`. Use the `id` from `GET /api/movies/` as the value for `movie_id`.

Add favorite example:

```json
{
  "movie_id": 1
}
```

---

## 📺 Watchlist

* **Add to Watchlist (Authenticated)** → `POST /api/users/{user_id}/watchlist/`
* **List My Watchlist (Authenticated)** → `GET /api/users/{user_id}/watchlist/`
* **Remove from Watchlist (Owner/Admin)** → `DELETE /api/users/{user_id}/watchlist/{id}/`

Add to watchlist example:

```json
{
  "movie_id": 1
}
```

---

## ⭐ Ratings

* **Rate a Movie (Authenticated)** → `POST /api/users/{user_id}/ratings/`
* **List My Ratings (Authenticated)** → `GET /api/users/{user_id}/ratings/`
* **Update Rating (Owner/Admin)** → `PATCH /api/users/{user_id}/ratings/{id}/`
* **Delete Rating (Owner/Admin)** → `DELETE /api/users/{user_id}/ratings/{id}/`

> Notes: Rating must be between 0 and 5. Each user can only rate a movie once — use `PATCH` to update an existing rating. Movies rated 4 or above feed the ratings-based recommendation engine.

Rate a movie example:

```json
{
  "movie_id": 2,
  "rating": 5
}
```

Update rating example:

```json
{
  "rating": 4.5
}
```

---

## 🔍 Search History

Search history is a log of what the user has searched for. It feeds into the recommendation engine.

* **Add Search Entry (Authenticated)** → `POST /api/searches/`
* **List My Search History (Authenticated)** → `GET /api/searches/`
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

Two recommendation strategies are supported — both use the user's own behaviour to personalize results. Both endpoints are `GET` only and require no request body.

### From Search History

**GET** `/api/generated-recommendations/from-search-history/`

Reads the user's recent search queries, extracts keywords, searches TMDB using those terms, saves results locally, excludes movies already rated/favorited/watchlisted, caches the result, and returns a ranked movie list.

> Best when the user has active search history. Requires at least one logged search entry. Returns up to 10 movies.

Response example:

```json
[
  {
    "id": 21,
    "tmdb_id": 62,
    "title": "2001: A Space Odyssey",
    "poster_path": "/ve72VxNqjGM69Uky4WTo2bK6rfq.jpg",
    "release_date": "1968-04-02",
    "cached_at": "2026-04-28T15:05:22.673793Z"
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

Reads movies the user rated 4 or above, fetches TMDB recommendations based on each liked movie, merges and ranks results by frequency of appearance, excludes already interacted movies, caches the result, and returns a ranked movie list.

> Best when the user has rated several movies. Requires at least one movie rated 4 or above. More stable and accurate than search-based recommendations.

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

2. Register a user → `POST /api/register/` *(welcome email sent automatically via Celery)*
3. Login → `POST /api/token/` → copy your `access` token
4. Load trending movies → `GET /api/movies/` — **do this first**, it populates local movie IDs
5. Add favorites → `POST /api/users/{user_id}/favorites/` with `{ "movie_id": 1 }`
6. Add to watchlist → `POST /api/users/{user_id}/watchlist/` with `{ "movie_id": 2 }`
7. Rate movies → `POST /api/users/{user_id}/ratings/` with `{ "movie_id": 2, "rating": 5 }`
8. Log searches → `POST /api/searches/` with `{ "query": "space adventure" }`
9. Get recommendations:
   * `GET /api/generated-recommendations/from-search-history/`
   * `GET /api/generated-recommendations/from-ratings/`
10. Check cached results → `GET /api/recommendations/`
11. 🧪 Check Celery logs for background task execution:

```bash
docker compose logs -f celery
```

> **Dependency chain:** Favorites, watchlist, and ratings all reference local movie `id` values that only exist after `GET /api/movies/` has been called at least once. Recommendations only return results when sufficient data exists — at least one logged search for search-history recommendations, and at least one movie rated 4 or above for ratings-based recommendations.

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
EMAIL_HOST_USER=your_email@yourdomain.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@yourdomain.com

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
* Builds the image and tags it as `latest`
* Pushes the tag to Docker Hub: `kiprotich507/movie-recommendation-backend`

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
Checkout → Setup Python Environment → Run Tests → Build Docker Image → Push Docker Image
```

* **Checkout** — pulls repo from GitHub using `github-credentials`
* **Setup Python Environment** — installs `gcc`, `libpq-dev`, `docker.io`, and all Python dependencies inside a `python:3.12` Docker agent; also installs `pytest-django` for Django-aware test discovery
* **Run Tests** — runs `pytest --junitxml=report.xml` using the SQLite override so no Postgres sidecar is needed; JUnit report is published to the Jenkins dashboard
* **Build Docker Image** — resolves the Git commit SHA directly in the shell (`IMAGE_TAG=$(git rev-parse --short HEAD)`), then builds and tags as both `latest` and `<commit-hash>`
* **Push Docker Image** — resolves the commit SHA in the shell again and pushes both tags to Docker Hub using `docker-credentials`

> **Note on secure interpolation:** All `sh` blocks in the Jenkinsfile use single-quoted strings (`'''...'''`) so Groovy never interpolates sensitive variables. Shell environment variables are resolved by the shell instead, which is the Jenkins-recommended pattern. The commit hash is also resolved in the shell for the same reason — passing it through Groovy's `env` caused it to always remain `latest` regardless of the actual hash.

### pytest Configuration

`pytest.ini` at the project root tells pytest where to find the Django settings module and which files to treat as test files:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = movie_recommendation_backend.settings
python_files = tests.py test_*.py *_tests.py
```

Without this file, pytest cannot discover Django tests because it does not know the settings module and does not match the `tests.py` naming convention by default. `pytest-django` must also be installed — it is listed in `requirements.txt`.

### SQLite Override for Jenkins Tests

The Jenkins pipeline runs tests inside a `python:3.12` Docker agent with no Postgres available. To avoid needing a database sidecar, `settings.py` is configured in two parts.

First, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` are given empty string defaults so `settings.py` loads without crashing when those variables are absent:

```python
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env('DB_NAME', default=''),
        "USER": env('DB_USER', default=''),
        "PASSWORD": env('DB_PASSWORD', default=''),
        "HOST": env('DB_HOST', default='db'),
        "PORT": env('DB_PORT', default='5432'),
    }
}
```

Then, after the Postgres block, the database is overridden to SQLite when `USE_SQLITE_FOR_TESTS` is set:

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

Without the `default=''` values, `settings.py` would crash on the Postgres block before ever reaching the SQLite override, since `django-environ` raises an error for missing required variables.

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

## ☸️ Kubernetes Deployment

This project includes a full local Kubernetes deployment using **Minikube**, covering cluster setup, app deployment, scaling, ingress, blue-green deployment, and rolling updates. All Kubernetes manifests and shell scripts live at the project root alongside the `Dockerfile` and `Jenkinsfile` — not inside the Django app folders, which are reserved for application and project configuration code.

The Kubernetes setup is the natural next layer after Docker Compose and CI/CD: Docker Compose handles local development, Jenkins and GitHub Actions handle build and delivery, and Kubernetes handles orchestration and deployment strategy.

**Environment config in Kubernetes:** Docker Compose reads `.env` automatically. Kubernetes does not. Non-sensitive values (debug mode, database name, email host, Redis URLs) are injected via a `ConfigMap`. Sensitive values (Django secret key, database password, TMDB API key, email app password) are injected via a `Secret`. Neither file with real values is committed to GitHub.

**Database in Kubernetes:** `DB_HOST=db` works in Docker Compose because Compose creates a service named `db`. In Kubernetes, a dedicated PostgreSQL `Deployment` and a `Service` named `db` must exist for the same hostname to resolve inside the cluster.

**Startup ordering:** Kubernetes does not guarantee that dependent services are ready before the app pod starts. The Django container handles this with a wait loop built directly into its startup command in `deployment.yaml` — it calls `nc -z db 5432` every 2 seconds until Postgres is reachable, then runs `python manage.py migrate` and starts the server. The pod stays running and waiting rather than crashing, so no manual intervention is needed on first boot.

**`ALLOWED_HOSTS` in Kubernetes:** Django rejects requests from hosts not listed in `ALLOWED_HOSTS`. The project hardcodes the required hosts directly in `settings.py`:

```python
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "movie.local"]
```

This covers port-forward access (`127.0.0.1`), Ingress access (`movie.local`), and the container bind address (`0.0.0.0`). No `ALLOWED_HOSTS` configuration is needed in `configmap.yaml`.

**Code changes and running pods:** Kubernetes runs containers from Docker images, not from local source files. Editing `settings.py` or any other file locally has no effect on running pods until the image is rebuilt, pushed to Docker Hub, and the deployments are restarted.

---

### 🗂️ Kubernetes File Reference

Files are listed in workflow order — the order you apply and use them.

| File | Kind | Purpose |
| --- | --- | --- |
| `kurbeScript` | Shell script | Starts Minikube, verifies cluster, lists pods |
| `configmap.yaml` | ConfigMap | Non-sensitive environment variables |
| `secret.example.yaml` | Secret template | Safe-to-commit template showing Secret structure |
| `postgres-deployment.yaml` | Deployment | Runs PostgreSQL inside the cluster |
| `postgres-service.yaml` | Service | Gives PostgreSQL the stable hostname `db` |
| `deployment.yaml` | Deployment | Runs the Django app |
| `service.yaml` | Service | Exposes Django internally via ClusterIP |
| `kubctl-0x01` | Shell script | Scales to 3 replicas, checks pods and resource usage |
| `ingress.yaml` | Ingress | Routes external HTTP traffic to the Django service |
| `commands.txt` | Reference | Commands used to apply the Ingress configuration |
| `blue_deployment.yaml` | Deployment | Blue (current stable) version for blue-green strategy |
| `green_deployment.yaml` | Deployment | Green (new) version deployed alongside blue |
| `kubeservice.yaml` | Service | Switches traffic between blue and green via selector |
| `kubctl-0x02` | Shell script | Applies blue-green deployment and inspects green logs |
| `kubctl-0x03` | Shell script | Applies rolling update, monitors rollout, tests availability |

> `secret.yaml` (with real values) is added to `.gitignore` and never committed. Only `secret.example.yaml` is in the repository.

---

### 🚀 Running the Cluster

Start Minikube and verify the cluster:

```bash
./kurbeScript
```

This checks that `minikube` and `kubectl` are installed, starts Minikube with the Docker driver, runs `kubectl cluster-info`, and lists all pods across namespaces.

---

### ⚙️ Environment Configuration

Apply config before deploying any workload, because both the Django and PostgreSQL Deployments depend on these resources existing first:

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

`configmap.yaml` holds non-sensitive values — `DEBUG`, `DB_NAME`, `DB_HOST`, `DB_PORT`, email host settings, and Redis/Celery URLs. `secret.yaml` holds sensitive values — `SECRET_KEY`, `DB_PASSWORD`, `TMDB_API_KEY`, and `EMAIL_HOST_PASSWORD`.

Both are loaded into the Django pod using `envFrom` in `deployment.yaml`:

```yaml
envFrom:
  - configMapRef:
      name: movie-app-config
  - secretRef:
      name: movie-app-secret
```

---

### 🐘 PostgreSQL in Kubernetes

Deploy the database and its Service before the Django app, so `db` is resolvable when Django starts:

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
```

`postgres-service.yaml` creates a `ClusterIP` Service named `db`. This is the exact name `DB_HOST=db` resolves to inside the cluster. Without this Service, Django pods fail immediately with a DNS resolution error on startup.

---

### 🌐 Deploying the App

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods
kubectl get services
kubectl logs <pod-name>
```

`service.yaml` exposes the Django app internally using `ClusterIP`. This keeps the app unreachable from outside the cluster until an Ingress is configured, which matches real production patterns where backends are not directly exposed.

If you ever need to force a pod to re-run the wait loop and pick up a config change (for example after updating a Secret), restart the deployment manually:

```bash
kubectl rollout restart deployment movie-app
kubectl get pods -w
kubectl logs -l app=movie-app
```

---

### 📈 Scaling

```bash
./kubctl-0x01
```

Scales the `movie-app` deployment to 3 replicas, then verifies running pods and resource usage via `kubectl top pods`. Because the Service is `ClusterIP`, load testing uses port-forwarding:

```bash
kubectl port-forward service/movie-service 8000:80
# then in another terminal:
wrk http://127.0.0.1:8000
```

Enable the metrics server if `kubectl top` is unavailable:

```bash
minikube addons enable metrics-server
```

---

### 🌍 Ingress

```bash
minikube addons enable ingress
kubectl apply -f ingress.yaml
kubectl get ingress
```

`ingress.yaml` routes traffic from `movie.local` to `movie-service` on port 80. Add the Minikube IP to `/etc/hosts` to resolve the domain locally:

```bash
echo "$(minikube ip) movie.local" | sudo tee -a /etc/hosts
```

Then test:

```bash
curl http://movie.local/api/
```

> **Note on URLs:** `0.0.0.0` is the address Django *binds to* inside the container — it means "listen on all interfaces." It is not a valid address to access from outside the container. Use `http://127.0.0.1:<port>` for port-forward access and `http://movie.local` for Ingress access.

---

### 🟦🟩 Blue-Green Deployment

```bash
./kubctl-0x02
```

Applies `blue_deployment.yaml` (current stable version, image tag `latest`) and `green_deployment.yaml` (new version, image tag `2.0`) simultaneously. `kubeservice.yaml` controls which version receives traffic via its `version` label selector — starting with `version: blue`.

To switch traffic to the green version, change the selector in `kubeservice.yaml`:

```yaml
selector:
  app: movie-app
  version: green   # was: blue
```

Then apply:

```bash
kubectl apply -f kubeservice.yaml
```

The script also waits for the green rollout to complete and reads logs from a running green pod to confirm the new version started correctly.

> The `2.0` image must exist on Docker Hub before the green deployment can pull it. Build and push it first:
> ```bash
> docker build -t kiprotich507/movie-recommendation-backend:2.0 .
> docker push kiprotich507/movie-recommendation-backend:2.0
> ```

> **Keeping `2.0` in sync with your code:** `dep.yml` pushes `latest` automatically on every push to `main`. The `2.0` tag is a manual one-time push that simulates a new release for the blue-green exercise. If you have made code changes and want green to reflect them, rebuild and push `2.0` manually, then restart the green deployment:
> ```bash
> docker build -t kiprotich507/movie-recommendation-backend:2.0 .
> docker push kiprotich507/movie-recommendation-backend:2.0
> kubectl rollout restart deployment movie-app-green
> ```

---

### 🔄 Rolling Updates

```bash
./kubctl-0x03
```

Applies the updated `blue_deployment.yaml`, monitors rollout with `kubectl rollout status`, then uses `kubectl port-forward` with a `curl` loop against `/api/` to verify the service remains available throughout the update. All 10 requests returning `HTTP 200 OK` confirms zero downtime during the rollout.

The rolling update strategy in `blue_deployment.yaml` replaces old pods with new ones gradually. Kubernetes' default `RollingUpdate` strategy ensures at least one pod stays available while new pods are scheduled.

---

### 🐛 Debugging & Common Issues

**Pod logs show `could not translate host name "db"`**
The wait loop in `deployment.yaml` retries `nc -z db 5432` every 2 seconds until Postgres is reachable, so this should not occur on current pods. If you see it — for example after manually creating a pod outside the normal deployment — confirm the Postgres Service exists and force a restart:

```bash
kubectl get services
kubectl rollout restart deployment movie-app
kubectl get pods -w
```

**Deployment unchanged after editing a YAML file**
If `kubectl apply` reports `unchanged` but you want to force a pod restart (for example after updating a Secret or ConfigMap):

```bash
kubectl rollout restart deployment movie-app
```

This works for any deployment — replace `movie-app` with `movie-app-blue`, `movie-app-green`, or `postgres` as needed.

**Green pods stuck in `ImagePullBackOff`**
The `2.0` image does not exist on Docker Hub yet. Build and push it manually first, then restart:

```bash
docker build -t kiprotich507/movie-recommendation-backend:2.0 .
docker push kiprotich507/movie-recommendation-backend:2.0
kubectl rollout restart deployment movie-app-green
```

**Green pods running stale code after changes**
`dep.yml` only pushes `latest` automatically. The `2.0` tag must be updated manually whenever you want green to reflect current code:

```bash
docker build -t kiprotich507/movie-recommendation-backend:2.0 .
docker push kiprotich507/movie-recommendation-backend:2.0
kubectl rollout restart deployment movie-app-green
```

**`kubectl top pods` returns `Metrics API not available`**
The metrics server is not yet ready. Enable it and wait for the pod to reach `Running`:

```bash
minikube addons enable metrics-server
kubectl get pods -n kube-system -w
```

Once `metrics-server` shows `1/1 Running`, `kubectl top pods` will work.

**Ingress addon fails with `context deadline exceeded`**
The ingress-nginx pods did not become ready in time, usually due to a slow image pull. Disable and re-enable, optionally with more resources:

```bash
minikube addons disable ingress
minikube stop
minikube start --driver=docker --cpus=4 --memory=4096
minikube addons enable ingress
kubectl get pods -n ingress-nginx -w
```

**`curl` against `movie-bluegreen-service` returns malformed URL**
The Service is `ClusterIP` so `minikube service --url` does not produce a valid URL. Use port-forwarding instead:

```bash
kubectl port-forward service/movie-bluegreen-service 8001:80
# in another terminal:
curl http://127.0.0.1:8001/api/
```

**Checking which image a running pod is using**

```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].image}'
```

**Useful one-liners**

```bash
# watch all pods live
kubectl get pods -w

# stream logs from all app pods
kubectl logs -l app=movie-app -f

# describe a pod for detailed events and errors
kubectl describe pod <pod-name>

# delete a stuck terminating pod
kubectl delete pod <pod-name> --force --grace-period=0

# check all services and their cluster IPs
kubectl get services

# check events across the namespace (good for pull errors, scheduling issues)
kubectl get events --sort-by='.lastTimestamp'
```

---

### 🔁 Full Apply Order

```bash
./kurbeScript

kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml

kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

minikube addons enable metrics-server
./kubctl-0x01

minikube addons enable ingress
kubectl apply -f ingress.yaml

./kubctl-0x02
./kubctl-0x03
```

---

### 🔐 Kubernetes Secrets vs Docker Compose `.env`

| Context | How variables are provided |
| --- | --- |
| Local development (Docker Compose) | `.env` file, read automatically |
| GitHub Actions CI | `env:` block + GitHub Secrets |
| Jenkins | `environment {}` block + Jenkins credentials |
| Kubernetes | `ConfigMap` + `Secret`, injected via `envFrom` |

In all cases, sensitive values are never hardcoded in committed files. The pattern is consistent across the full stack.

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
