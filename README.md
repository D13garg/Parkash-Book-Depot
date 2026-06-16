# Parkash Book Depot — Full Stack Platform

A production-grade bookstore management system combining inventory management, customer project requests, internal operations, observability, and AI tooling via MCP.

**Live:** https://parkash-book-depot.vercel.app  
**Backend:** Railway (FastAPI + MongoDB)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| State | Zustand (persisted), TanStack Query v5 |
| Forms | React Hook Form + Zod |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| Database | MongoDB (Motor async driver) |
| Auth | JWT (access + refresh tokens), bcrypt + pepper, Google OAuth |
| Email | Resend API (OTP verification, password reset) |
| Storage | Cloudinary (gallery images) |
| Deploy | Vercel (frontend), Railway (backend) |
| CI/CD | GitHub Actions (backend tests + frontend build on every push) |
| Developer Tools | CLI (Typer + Rich + httpx), MCP Server (FastMCP), Chrome Extension |

---

## Project Structure

```
Parkash-Book-Depot/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── scripts/
│   │   ├── seed_admin.py
│   │   └── create_associate.py
│   ├── tests/
│   └── app/
│       ├── core/
│       │   ├── config.py               # pydantic-settings, all env vars
│       │   ├── database.py             # Motor singleton + lifecycle
│       │   ├── security.py             # JWT, bcrypt + pepper, password strength
│       │   ├── enums.py                # roles, statuses, state machines
│       │   ├── exceptions.py           # AppException hierarchy + TooManyRequestsException
│       │   ├── email_validation.py     # disposable email blocking
│       │   └── create_indexes.py       # MongoDB indexes + TTL (otps, error_logs)
│       ├── models/
│       │   ├── user.py                 # hashed_password Optional (Google OAuth)
│       │   ├── book.py
│       │   ├── order.py
│       │   ├── otp.py                  # bcrypt-hashed code, expiry, attempts counter
│       │   ├── project_request.py
│       │   ├── project.py
│       │   ├── project_update.py
│       │   ├── review.py               # created_at + updated_at
│       │   ├── gallery.py
│       │   ├── notification.py
│       │   ├── audit_log.py
│       │   ├── error_log.py
│       │   └── metrics.py
│       ├── schemas/
│       │   ├── user.py                 # RegisterInitiateRequest, OTPVerifyRequest,
│       │   │                           # ForgotPasswordVerifyRequest, GoogleAuthRequest
│       │   ├── book.py
│       │   ├── order.py
│       │   ├── project_request.py
│       │   ├── project.py
│       │   ├── review.py               # UpdateReviewRequest added
│       │   ├── gallery.py
│       │   ├── notification.py
│       │   ├── audit_log.py
│       │   ├── error_log.py
│       │   ├── metrics.py
│       │   └── analytics.py
│       ├── repositories/
│       │   ├── book_repository.py      # decrement_stock_atomic, increment_stock_atomic
│       │   ├── review_repository.py    # update, delete methods
│       │   └── ...all other repos
│       ├── services/
│       │   ├── auth_service.py         # register (2-step OTP), login, Google OAuth,
│       │   │                           # forgot password (OTP), refresh token
│       │   ├── book_service.py
│       │   ├── order_service.py        # cancel_order with stock restore,
│       │   │                           # atomic stock on place + cancel
│       │   ├── otp_service.py          # generate, hash, verify; rate limiting;
│       │   │                           # brute force protection (5 attempts max)
│       │   ├── email_service.py        # Resend API, styled HTML email templates
│       │   ├── project_request_service.py
│       │   ├── project_service.py
│       │   ├── review_service.py       # edit + delete, timestamp fix
│       │   ├── gallery_service.py
│       │   ├── notification_service.py
│       │   ├── audit_log_service.py
│       │   ├── error_log_service.py
│       │   ├── metrics_service.py
│       │   └── analytics_service.py
│       ├── permissions/
│       ├── dependencies/
│       ├── middleware/
│       │   ├── security_headers.py     # CSP, X-Frame-Options, HSTS, etc.
│       │   └── ...
│       └── api/v1/endpoints/
│           ├── auth.py                 # /register/initiate, /register/verify,
│           │                           # /login, /forgot-password/initiate,
│           │                           # /forgot-password/verify, /google, /refresh, /me
│           ├── users.py                # GET /users, GET /users/associates,
│           │                           # PATCH /{id}/deactivate, PATCH /{id}/reactivate
│           ├── books.py
│           ├── orders.py               # includes PATCH /{id}/cancel (customer)
│           ├── reviews.py              # PATCH /{id}, DELETE /{id} added
│           └── ...all other endpoints
│
├── parkash_mcp/                        # MCP Server — AI client integration
│   ├── server.py                       # FastMCP entry point, registers all tools
│   ├── context.py                      # MongoDB lifecycle + MCP_USER synthetic identity
│   ├── adapter.py                      # AppException → MCP error string translator
│   └── tools/
│       ├── books.py                    # list_books, get_book, get_low_stock_books,
│       │                               # create_book, update_book, update_book_stock
│       ├── orders.py                   # list_all_orders, get_order, update_order_status
│       ├── users.py                    # list_users, list_associates,
│       │                               # deactivate_user, reactivate_user
│       ├── projects.py                 # list_project_requests, get_project_request,
│       │                               # update_request_status, convert_request_to_project,
│       │                               # list_projects, get_project, get_project_updates,
│       │                               # assign_project_associate, update_project_status,
│       │                               # add_project_update
│       ├── reviews.py                  # list_reviews, delete_review (confirm=True required)
│       └── observability.py            # ping, get_analytics, get_metrics_summary,
│                                       # get_metrics_trend, get_audit_logs,
│                                       # get_entity_audit_logs, get_error_logs
│
├── cli/                                # Developer CLI
│   ├── main.py                         # typer app: auth login/logout, config
│   ├── http.py                         # sync httpx ApiClient, ApiError
│   ├── config.py                       # ~/.config/parkash-cli/config.json (chmod 600)
│   └── commands/
│       ├── books.py
│       ├── orders.py
│       └── users.py
│
├── extension/                          # Chrome Extension — "Add to Parkash" button
│   ├── manifest.json                   # Manifest V3
│   ├── background.js                   # service worker, opens dashboard with URL params
│   ├── content/
│   │   ├── amazon.js                   # scraper for Amazon India
│   │   ├── flipkart.js                 # scraper for Flipkart
│   │   ├── google_books.js             # scraper for Google Books
│   │   └── snapdeal.js                 # scraper for Snapdeal
│   ├── inject/
│   │   └── autofill.js                 # injected on /admin/books/add, fills form fields
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
│
└── frontend/
    ├── vercel.json                     # security headers (CSP, X-Frame, HSTS, etc.)
    └── src/
        ├── auth/pages/
        │   ├── LoginPage.tsx           # email/password + Google Sign-In button
        │   ├── RegisterPage.tsx        # step 1: fill form → sends OTP
        │   ├── VerifyOTPPage.tsx       # step 2: 4-digit OTP (register + forgot password)
        │   └── ForgotPasswordPage.tsx
        ├── customer/pages/
        │   ├── BooksPage.tsx           # browse, search, filter, book detail drawer
        │   ├── CartPage.tsx
        │   ├── MyOrdersPage.tsx        # order history + cancel button (pending/confirmed)
        │   ├── MyReviewPage.tsx        # view + inline edit + delete reviews
        │   ├── SubmitReviewPage.tsx
        │   └── ...all other pages
        ├── associate/pages/
        ├── admin/pages/
        │   ├── AdminProjectDetailPage.tsx  # assign by name dropdown (useAssociates)
        │   ├── AdminUsersPage.tsx          # deactivate/reactivate, stat cards
        │   └── ...all other pages
        └── shared/
            ├── hooks/
            │   ├── useAuth.ts          # login, registerInitiate/Verify,
            │   │                       # forgotPassword, googleAuth, logout
            │   ├── useAssociates.ts    # GET /users/associates for admin dropdown
            │   ├── useOrders.ts        # includes useCancelOrder
            │   ├── useReviews.ts       # includes useUpdateReview, useDeleteReview
            │   └── ...all other hooks
            └── stores/
                ├── authStore.ts        # Zustand, persisted to localStorage
                └── cartStore.ts        # Zustand, persisted, qty capped to stock
```

---

## User Roles

| Role | Access |
|------|--------|
| **Customer** | Browse books, cart + orders, cancel orders (pending/confirmed), submit requests, write/edit/delete reviews, view gallery |
| **Associate** | Assigned projects only, add progress updates, change project status |
| **Admin** | Full access — books, orders, projects, users, reviews, gallery, analytics, observability |

---

## Authentication Flow

### Email Registration (2-step OTP)
```
1. POST /auth/register/initiate  — validate, hash password, send 4-digit OTP via Resend
2. POST /auth/register/verify    — verify OTP → create account → return JWT tokens
```

### Forgot Password
```
1. POST /auth/forgot-password/initiate  — send OTP (silent if email not found)
2. POST /auth/forgot-password/verify    — verify OTP + new password → update hash
```

### Google OAuth
```
Frontend loads Google Identity Services → user clicks button → Google returns id_token
→ POST /auth/google — verified with google-auth library → create/find account → return tokens
```

### OTP Security Model
- Cryptographically secure 4-digit codes (`secrets.randbelow`)
- Stored as **bcrypt hash** — never plain text in DB
- **Single-use** — burned immediately on first successful verify
- **3-minute expiry** — MongoDB TTL index auto-deletes
- **Max 5 wrong attempts** — OTP invalidated after lockout
- **Max 3 sends per email per hour** — flood protection
- Constant-time bcrypt comparison — no timing attacks

---

## API Endpoints

| Module | Prefix |
|--------|--------|
| Auth | `/api/v1/auth` |
| Users | `/api/v1/users` |
| Books | `/api/v1/books` |
| Orders | `/api/v1/orders` |
| Project Requests | `/api/v1/project-requests` |
| Projects | `/api/v1/projects` |
| Reviews | `/api/v1/reviews` |
| Gallery | `/api/v1/gallery` |
| Notifications | `/api/v1/notifications` |
| Audit Logs | `/api/v1/audit-logs` |
| Error Logs | `/api/v1/error-logs` |
| Metrics | `/api/v1/metrics` |
| Analytics | `/api/v1/analytics` |

---

## Security

| Feature | Detail |
|---------|--------|
| JWT | Access token (30 min) + refresh token (3 days) |
| Passwords | bcrypt + pepper, strength enforced |
| OTP | bcrypt-hashed, single-use, 3-min TTL, 5-attempt lockout |
| Google OAuth | Verified via `google-auth` library (signature + expiry + audience) |
| Rate limiting | slowapi — 5/min register initiate, 10/min login, 5/min OTP |
| Security headers | CSP, X-Frame-Options (DENY), HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy — set on both Railway and Vercel |
| RBAC | Role + ownership checks on every sensitive endpoint |
| Stock race condition | Atomic `findOneAndUpdate` with `$inc` and floor check — prevents overselling |
| Docs | Swagger UI + OpenAPI disabled in production |

---

## Observability

| Layer | Retention | Notes |
|-------|-----------|-------|
| Audit Logs | Permanent | Every important action, all services, includes MCP Server actor |
| Error Logs | 7 days | MongoDB TTL auto-deletes |
| Metrics | Permanent | Hourly counters, 30-day trend |
| Analytics | On-demand | Revenue, top books, request funnel — no storage |

---

## MongoDB Collections

```
users  books  orders  otps  project_requests  projects
project_updates  reviews  gallery  notifications
audit_logs  error_logs  metrics_hourly
```

---

## State Machines

**Order:** `pending → confirmed → processing → shipped → delivered`  
Customer or admin can cancel from `pending` or `confirmed`. Stock atomically restored on any cancellation.

**Project Request:** `submitted → under_review → accepted/rejected → converted_to_project`

**Project:** `pending → assigned → in_progress → waiting_supplier → completed/cancelled`

---

## MCP Server (32 tools)

**Architecture:** `MCP tools → internal services → repositories → MongoDB` (no HTTP, no JWT)

All write actions attributed to `MCP Server` identity in audit log.

```bash
cd Parkash-Book-Depot
python -m parkash_mcp.server
```

Claude Desktop config (`~/.claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "parkash-book-depot": {
      "command": "python",
      "args": ["-m", "parkash_mcp.server"],
      "cwd": "/path/to/Parkash-Book-Depot",
      "env": {
        "MONGODB_URL": "...",
        "MONGODB_DB_NAME": "parkash_book_depot",
        "SECRET_KEY": "...",
        "PEPPER": "...",
        "CLOUDINARY_CLOUD_NAME": "...",
        "CLOUDINARY_API_KEY": "...",
        "CLOUDINARY_API_SECRET": "...",
        "RESEND_API_KEY": "...",
        "EMAIL_FROM": "...",
        "GOOGLE_CLIENT_ID": "...",
        "GOOGLE_CLIENT_SECRET": "..."
      }
    }
  }
}
```

| Domain | Tools |
|--------|-------|
| Books | `list_books`, `get_book`, `get_low_stock_books`, `create_book`, `update_book`, `update_book_stock` |
| Orders | `list_all_orders`, `get_order`, `update_order_status` |
| Users | `list_users`, `list_associates`, `deactivate_user`, `reactivate_user` |
| Projects | `list_project_requests`, `get_project_request`, `update_request_status`, `convert_request_to_project`, `list_projects`, `get_project`, `get_project_updates`, `assign_project_associate`, `update_project_status`, `add_project_update` |
| Reviews | `list_reviews`, `delete_review` (requires `confirm=True`) |
| Observability | `ping`, `get_analytics`, `get_metrics_summary`, `get_metrics_trend`, `get_audit_logs`, `get_entity_audit_logs`, `get_error_logs` |

---

## Developer CLI

```bash
cd cli && pip install typer rich httpx

python -m cli.main auth login --email admin@example.com
python -m cli.main books list --search "NCERT"
python -m cli.main orders list --status pending
python -m cli.main users list
```

Tokens stored at `~/.config/parkash-cli/config.json` (chmod 600).

---

## Chrome Extension — "Add to Parkash"

Scrapes book details from Amazon India, Flipkart, Google Books, Snapdeal and auto-fills the admin Add Book form.

**Install:**
1. `chrome://extensions/` → Enable Developer mode
2. Load unpacked → select `extension/` folder

**Usage:** Open any book page on a supported site → click amber **"📚 Add to Parkash Book Depot"** button → dashboard opens with all fields pre-filled.

**Scraped fields:** title, authors, publisher, ISBN, description, language, price, categories, edition

---

## Local Setup

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_admin.py
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## Environment Variables

### Railway (Backend)
```
SECRET_KEY=<min 32 chars>
PEPPER=<min 32 chars>
MONGODB_URL=<Atlas connection string>
MONGODB_DB_NAME=parkash_book_depot
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://your-vercel-url.vercel.app"]
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
RESEND_API_KEY=
EMAIL_FROM=noreply@yourdomain.com
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Vercel (Frontend)
```
VITE_API_URL=https://your-backend.railway.app/api/v1
VITE_GOOGLE_CLIENT_ID=<same as Railway GOOGLE_CLIENT_ID>
```

---

## Tests

```bash
cd backend && pytest tests/ -v
```

Covers: security utilities, state machine transitions, RBAC permissions.

---

*Built with FastAPI + React. Deployed on Railway + Vercel.*