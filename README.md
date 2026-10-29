# Budget Tracker

REST API for tracking income and expenses by category, with monthly budgets, a monthly summary and CSV import. Built with FastAPI, PostgreSQL, SQLAlchemy and Alembic.


## Configuration

The `.env` file is not in the repository. Create it from the example before running anything:

```bash
cp .env.example .env
```

The default values in `.env.example` work without changes.


## Run with Docker

Requires Docker Desktop (or Docker Engine with Compose) to be running.

```bash
cp .env.example .env          # Windows: Copy-Item .env.example .env
docker compose up -d --build
```

- API: http://localhost:8000
- API documentation (OpenAPI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

Migrations run automatically on start. Stop with `docker compose down`.

## Run without Docker (optional)

With the virtual environment from [Run the tests](#run-the-tests) activated:

```bash
docker compose up -d --wait db
alembic upgrade head
uvicorn app.main:app --reload
```

## Run the tests

Requires Python 3.12 and the `.env` file from the previous section. Run from the project root:

```bash
python -m venv .venv          # Linux / macOS: python3 -m venv .venv
.venv\Scripts\Activate.ps1    # Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d db
docker compose exec db createdb -U postgres budget_tracker_test 

python -m pytest
```

Tests use a separate database (`budget_tracker_test`), so the main database is not affected.

## Endpoints

| Method | Path | Input | Output |
|---|---|---|---|
| `GET` | `/health` | – | status |
| `GET` | `/categories` | – | list of categories |
| `POST` | `/categories` | `name`, `color` | category |
| `PATCH` | `/categories/{id}` | `name`, `color` (optional) | category |
| `DELETE` | `/categories/{id}` | – | 204 |
| `GET` | `/transactions` | `page`, `page_size` | paginated transactions |
| `GET` | `/transactions/search` | `date_from`, `date_to`, `category_id`, `type`, `search`, `page`, `page_size` | paginated transactions |
| `GET` | `/transactions/{id}` | – | transaction |
| `POST` | `/transactions` | `type`, `amount`, `date`, `description`, `category_id` | transaction |
| `PATCH` | `/transactions/{id}` | any transaction field (optional) | transaction |
| `DELETE` | `/transactions/{id}` | – | 204 |
| `POST` | `/transactions/import` | CSV file (`file`) | imported count, failed rows with reasons |
| `GET` | `/budgets` | `month` (`YYYY-MM`) | list of budgets |
| `POST` | `/budgets` | `category_id`, `month`, `amount` | budget |
| `PUT` | `/budgets/{id}` | `amount` | budget |
| `DELETE` | `/budgets/{id}` | – | 204 |
| `GET` | `/summary` | `month` (`YYYY-MM`) | totals, balance, spent / budget / left per category |

Errors are returned as `{"message": "...", "details": [{"field": "...", "message": "..."}]}` with status `404`, `409` or `422`.