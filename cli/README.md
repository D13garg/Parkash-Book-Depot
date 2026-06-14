# Parkash CLI

Developer CLI for the Parkash Book Depot API. Uses Typer, httpx, and Rich.

## Setup

From the repository root:

```bash
pip install -e ./cli
```

Or with a virtual environment:

```bash
cd cli && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && python -m cli.main --help
```

## Local development

Start the backend first:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The CLI defaults to `http://localhost:8000/api/v1`.

Override with `--api-url` or `PARKASH_API_URL`:

```bash
parkash --api-url http://localhost:8000/api/v1 books list
```

## Authentication

Books list/get are public. Orders and users require a JWT.

```bash
parkash auth login
# or: PARKASH_ACCESS_TOKEN=... parkash orders list
```

Tokens are stored in `~/.config/parkash-cli/config.json` (mode 600).

## Commands

| Command | Endpoint | Auth |
|---------|----------|------|
| `parkash books list` | `GET /books` | Public |
| `parkash books get <id>` | `GET /books/{id}` | Public |
| `parkash orders list` | `GET /orders/mine` | User |
| `parkash orders list --all` | `GET /orders` | Admin |
| `parkash orders get <id>` | `GET /orders/{id}` | User (owner/admin) |
| `parkash users list` | `GET /users` | Admin |

## Examples

```bash
parkash books list --search python --page 1
parkash books get 507f1f77bcf86cd799439011
parkash auth login
parkash orders list
parkash orders list --all --status pending
parkash orders get 507f1f77bcf86cd799439011
parkash users list
```
