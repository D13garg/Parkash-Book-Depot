# Parkash Book Depot — Full Stack Platform

A production-grade bookstore management system combining inventory management, customer project requests, internal operations, observability, and AI tooling via MCP.

**Frontend:** Vercel
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
| Developer Tools | CLI (Typer + Rich + httpx), MCP Server (FastMCP) |

---

## Project Structure

```
Parkash-Book-Depot/
├── backend/
│   ├── main.py                          # uvicorn entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── scripts/
│   │   ├── seed_admin.py               # create first admin account
│   │   └── create_associate.py         # create associate accounts
│   ├── tests/
│   │   └── unit/
│   │       ├── test_security.py
│   │       ├── test_state_machines.py
│   │       └── test_permissions.py
│   └── app/
│       ├── main.py                      # FastAPI app factory + lifespan
│       ├── core/
│       │   ├── config.py               # pydantic-settings, all env vars
│       │   ├── database.py             # Motor singleton + lifecycle
│       │   ├── security.py             # JWT, bcrypt + pepper, password strength
│       │   ├── enums.py                # roles, statuses, state machines
│       │   ├── exceptions.py           # AppException hierarchy + TooManyRequestsException
│       │   ├── email_validation.py     # disposable email blocking
│       │   └── create_indexes.py       # MongoDB indexes + TTL (otps, error_logs)
│       ├── models/                      # MongoDB document shapes
│       │   ├── user.py                 # hashed_password Optional (Google OAuth)
│       │   ├── book.py
│       │   ├── order.py
│       │   ├── otp.py                  # OTP document (hashed code, expiry, attempts)
│       │   ├── project_request.py
│       │   ├── project.py
│       │   ├── project_update.py
│       │   ├── review.py               # includes updated_at
│       │   ├── gallery.py
│       │   ├── notification.py
│       │   ├── audit_log.py
│       │   ├── error_log.py
│       │   └── metrics.py
│       ├── schemas/                     # API request/response shapes
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
│       ├── repositories/                # MongoDB queries only, no business logic
│       │   ├── user_repository.py
│       │   ├── book_repository.py      # decrement_stock_atomic, increment_stock_atomic
│       │   ├── order_repository.py
│       │   ├── project_request_repository.py
│       │   ├── project_repository.py
│       │   ├── project_update_repository.py
│       │   ├── review_repository.py    # update, delete methods added
│       │   ├── gallery_repository.py
│       │   ├── notification_repository.py
│       │   ├── audit_log_repository.py
│       │   ├── error_log_repository.py
│       │   └── metrics_repository.py
│       ├── services/                    # all business logic lives here
│       │   ├── auth_service.py         # register (2-step OTP), login, Google OAuth,
│       │   │                           # forgot password (OTP), refresh token
│       │   ├── book_service.py
│       │   ├── order_service.py        # cancel_order with stock restore,
│       │   │                           # atomic stock on place + cancel
│       │   ├── otp_service.py          # generate, hash, verify OTPs; rate limiting;
│       │   │                           # brute force protection (5 attempts)
│       │   ├── email_service.py        # Resend API, styled HTML templates
│       │   ├── project_request_service.py
│       │   ├── project_service.py
│       │   ├── review_service.py       # edit + delete reviews, timestamp fix
│       │   ├── gallery_service.py
│       │   ├── notification_service.py
│       │   ├── audit_log_service.py    # audit() helper — silent, all services call it
│       │   ├── error_log_service.py    # log_error() helper — 7-day TTL
│       │   ├── metrics_service.py      # increment() helper — hourly counters
│       │   └── analytics_service.py   # pure aggregation, no storage
│       ├── permissions/
│       │   ├── role_permissions.py
│       │   ├── project_permissions.py
│       │   └── project_request_permissions.py
│       ├── dependencies/
│       │   ├── database.py             # get_db()
│       │   └── auth.py                 # get_current_user, get_current_admin
│       ├── middleware/
│       │   ├── logging.py
│       │   ├── security_headers.py     # CSP, X-Frame-Options, HSTS, etc.
│       │   ├── rate_limit.py           # slowapi
│       │   └── error_handler.py
│       └── api/v1/
│           ├── router.py
│           └── endpoints/
│               ├── health.py
│               ├── auth.py             # /register/initiate, /register/verify,
│               │                       # /login, /forgot-password/initiate,
│               │                       # /forgot-password/verify, /google, /refresh, /me
│               ├── users.py            # GET /users, GET /users/associates,
│               │                       # PATCH /users/{id}/deactivate,
│               │                       # PATCH /users/{id}/reactivate
│               ├── books.py
│               ├── orders.py           # includes PATCH /{id}/cancel (customer)
│               ├── project_requests.py
│               ├── projects.py
│               ├── reviews.py          # PATCH /{id}, DELETE /{id} added
│               ├── gallery.py
│               ├── notifications.py
│               ├── audit_logs.py
│               ├── error_logs.py
│               ├── metrics.py
│               └── analytics.py
│
├── parkash_mcp/                         # MCP server — AI client integration
│   ├── server.py                        # FastMCP entry point
│   ├── context.py                       # MCPContext wrapping CLI ApiClient
│   ├── adapter.py                       # exception translation, async thread wrapper
│   └── tools/
│       ├── health.py                    # health_check tool
│       ├── books.py                     # list_books, get_book tools
│       └── orders.py                    # list_orders, get_order tools
│                                        # ⚠ remaining 27 tools pending (see MCP section)
│
├── cli/                                 # Developer CLI
│   ├── main.py                          # typer app: auth login/logout, config
│   ├── http.py                          # sync httpx ApiClient, ApiError
│   ├── config.py                        # ~/.config/parkash-cli/config.json (chmod 600)
│   └── commands/
│       ├── books.py                     # parkash books list / get
│       ├── orders.py                    # parkash orders list / get
│       └── users.py                     # parkash users list
│
└── frontend/
    ├── vercel.json                      # security headers (CSP, X-Frame, HSTS, etc.)
    └── src/
        ├── auth/pages/
        │   ├── LoginPage.tsx            # email/password + Google Sign-In button
        │   ├── RegisterPage.tsx         # step 1: fill form → sends OTP
        │   ├── VerifyOTPPage.tsx        # step 2: 4-digit OTP entry (shared for
        │   │                            # register + forgot password)
        │   └── ForgotPasswordPage.tsx   # enter email → sends OTP
        ├── customer/pages/
        │   ├── CustomerDashboard.tsx
        │   ├── BooksPage.tsx            # browse, search, filter, book detail drawer
        │   ├── CartPage.tsx             # cart items, qty controls, checkout
        │   ├── MyOrdersPage.tsx         # order history + cancel button (pending/confirmed)
        │   ├── MyRequestsPage.tsx
        │   ├── SubmitRequestPage.tsx
        │   ├── MyReviewPage.tsx         # view + inline edit + delete reviews
        │   ├── SubmitReviewPage.tsx
        │   ├── GalleryPage.tsx
        │   ├── ContactUsPage.tsx
        │   └── ProfilePage.tsx
        ├── associate/pages/
        │   ├── AssociateDashboard.tsx
        │   ├── AssignedProjectsPage.tsx
        │   ├── ProjectDetailPage.tsx
        │   └── AddUpdatePage.tsx
        ├── admin/pages/
        │   ├── AdminDashboard.tsx
        │   ├── RequestQueuePage.tsx
        │   ├── AllProjectsPage.tsx
        │   ├── AdminProjectDetailPage.tsx  # assign by name dropdown (useAssociates)
        │   ├── AdminOrdersPage.tsx
        │   ├── BookManagementPage.tsx
        │   ├── AddBookPage.tsx
        │   ├── EditBookPage.tsx
        │   ├── AdminReviewsPage.tsx
        │   ├── AdminGalleryPage.tsx
        │   ├── AdminAuditLogsPage.tsx
        │   ├── AdminErrorLogsPage.tsx
        │   ├── AdminMetricsDashboard.tsx
        │   ├── AdminAnalyticsPage.tsx
        │   ├── AdminOrdersPage.tsx
        │   └── AdminUsersPage.tsx          # deactivate/reactivate users, stat cards
        └── shared/
            ├── components/
            │   ├── DashboardLayout.tsx
            │   ├── CartIcon.tsx
            │   ├── NotificationBell.tsx
            │   ├── StatusBadge.tsx
            │   ├── Pagination.tsx
            │   ├── LoadingSpinner.tsx
            │   ├── EmptyState.tsx
            │   ├── Skeletons.tsx
            │   └── Toast.tsx
            ├── hooks/
            │   ├── useAuth.ts           # login, registerInitiate/Verify,
            │   │                        # forgotPassword, googleAuth, logout
            │   ├── useBooks.ts
            │   ├── useOrders.ts         # useCancelOrder added
            │   ├── useAssociates.ts     # GET /users/associates for admin dropdown
            │   ├── useProjectRequests.ts
            │   ├── useProjects.ts
            │   ├── useReviews.ts        # useUpdateReview, useDeleteReview added
            │   ├── useGallery.ts
            │   ├── useNotifications.ts
            │   ├── useAdminRequests.ts
            │   ├── useAdminProjects.ts
            │   ├── useAdminBooks.ts
            │   ├── useAuditLogs.ts
            │   ├── useErrorLogs.ts
            │   ├── useMetrics.ts
            │   └── useAnalytics.ts
            ├── stores/
            │   ├── authStore.ts         # Zustand, persisted to localStorage
            │   └── cartStore.ts         # Zustand, persisted, qty capped to stock
            └── types/
                └── index.ts
```

---

## User Roles

| Role | Access |
|------|--------|
| **Customer** | Browse books, cart + orders, cancel orders, submit requests, write/edit/delete reviews, view gallery |
| **Associate** | Assigned projects only, add progress updates, change project status |
| **Admin** | Full access — books, orders, projects, users, reviews, gallery, analytics, observability |

---

## Authentication Flow

### Email Registration (2-step OTP)
```
1. POST /auth/register/initiate  — validate data, hash password, send 4-digit OTP via Resend
2. POST /auth/register/verify    — verify OTP → create account → return JWT tokens
```

### Forgot Password (OTP)
```
1. POST /auth/forgot-password/initiate  — send OTP (silent if email not found, prevents enumeration)
2. POST /auth/forgot-password/verify    — verify OTP + new password → update hash
```

### Google OAuth
```
Frontend loads Google Identity Services script → user clicks button → Google returns id_token
→ POST /auth/google  — verified with google-auth library (not tokeninfo endpoint)
→ creates account on first login, finds existing on subsequent logins
```

### OTP Security Model
- Codes are 4 digits, generated with `secrets.randbelow` (cryptographically secure)
- Stored as **bcrypt hash** — never plain text
- **Single-use** — burned immediately on verification
- **3-minute expiry** — MongoDB TTL index auto-deletes expired documents
- **Max 5 wrong attempts** before OTP is invalidated (brute force protection)
- **Max 3 sends per email per hour** (flood protection)
- Constant-time bcrypt comparison (no timing attacks)

---

## API Endpoints

| Module | Prefix | Key Endpoints |
|--------|--------|---------------|
| Auth | `/api/v1/auth` | register/initiate, register/verify, login, forgot-password/initiate, forgot-password/verify, google, refresh, me |
| Users | `/api/v1/users` | list all, associates, deactivate, reactivate |
| Books | `/api/v1/books` | CRUD, stock management, low-stock alert |
| Orders | `/api/v1/orders` | place, my orders, all orders (admin), update status, cancel (customer) |
| Project Requests | `/api/v1/project-requests` | submit, list, status update |
| Projects | `/api/v1/projects` | create, assign associate, status, updates timeline |
| Reviews | `/api/v1/reviews` | submit, edit, delete, my reviews, all reviews (admin) |
| Gallery | `/api/v1/gallery` | upload (Cloudinary), caption, delete |
| Notifications | `/api/v1/notifications` | list, mark read, unread count |
| Audit Logs | `/api/v1/audit-logs` | list with filters, by entity |
| Error Logs | `/api/v1/error-logs` | list with filters (7-day TTL) |
| Metrics | `/api/v1/metrics` | summary, 30-day trend |
| Analytics | `/api/v1/analytics` | full operational intelligence dashboard |

---

## Security

| Feature | Detail |
|---------|--------|
| JWT | Access token (30 min) + refresh token (3 days) |
| Passwords | bcrypt + pepper, strength enforced (upper, lower, digit, special) |
| OTP | bcrypt-hashed, single-use, 3-min TTL, 5-attempt lockout |
| Google OAuth | Verified via `google-auth` library (signature + expiry + audience) |
| Rate limiting | slowapi — 5/min register, 10/min login, 5/min OTP initiate |
| Security headers | CSP, X-Frame-Options (DENY), HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy — set on both Railway (API) and Vercel (frontend CDN) |
| RBAC | Role + ownership checks on every sensitive endpoint |
| Email validation | Blocks disposable/fake domains |
| Stock race condition | Atomic `findOneAndUpdate` with `$inc` and floor check — prevents overselling |
| Docs | Swagger UI and OpenAPI disabled in production |
| Request size | 5MB max |

---

## Observability

| Layer | Collection | Retention | Notes |
|-------|-----------|-----------|-------|
| Audit Logs | `audit_logs` | Permanent | Every important action, all services |
| Error Logs | `error_logs` | 7 days | MongoDB TTL index auto-deletes |
| Metrics | `metrics_hourly` | Permanent | Hourly counters, 30-day trend chart |
| Analytics | Aggregated on-demand | No storage | Revenue, top books, request funnel |

---

## MongoDB Collections

```
users           books           orders
otps            project_requests  projects
project_updates reviews         gallery
notifications   audit_logs      error_logs
metrics_hourly
```

---

## State Machines

**Project Request:**
```
submitted → under_review → accepted → converted_to_project
                        → rejected
```

**Project:**
```
pending → assigned → in_progress → waiting_supplier → completed
                                                    → cancelled
```

**Order:**
```
pending → confirmed → processing → shipped → delivered
       ↘ cancelled   ↘ cancelled
       (customer or admin)
```
Stock is atomically restored on any cancellation path.

---

## Developer CLI

```bash
cd cli
pip install typer rich httpx

# Authenticate
python -m cli.main auth login --email admin@example.com

# Books
python -m cli.main books list --search "NCERT" --in-stock-only
python -m cli.main books get <book_id>

# Orders
python -m cli.main orders list --all --status pending
python -m cli.main orders get <order_id>

# Users (admin)
python -m cli.main users list

# Config
python -m cli.main config
```

Tokens stored at `~/.config/parkash-cli/config.json` (chmod 600).  
Override API URL: `--api-url` flag or `PARKASH_API_URL` env var.

---

## MCP Server (AI Client Integration)

Exposes the bookstore to AI clients (Claude Desktop, Cursor, Windsurf, ChatGPT) via the Model Context Protocol.

**Architecture:** MCP tools → internal services → repositories → MongoDB (no HTTP round-trip)

**Current status:** Foundation complete. 5 tools live (health, list_books, get_book, list_orders, get_order). 27 tools pending.

**Planned tool inventory (32 total):**

| Domain | Tools |
|--------|-------|
| Health | `ping` |
| Books | `list_books`, `get_book`, `get_low_stock_books`, `create_book`, `update_book`, `update_book_stock` |
| Orders | `list_all_orders`, `get_order`, `update_order_status` |
| Users | `list_users`, `list_associates`, `deactivate_user`, `reactivate_user` |
| Projects | `list_project_requests`, `get_project_request`, `update_request_status`, `convert_request_to_project`, `list_projects`, `get_project`, `get_project_updates`, `assign_project_associate`, `update_project_status`, `add_project_update` |
| Reviews | `list_reviews`, `delete_review` |
| Observability | `get_analytics`, `get_metrics_summary`, `get_metrics_trend`, `get_audit_logs`, `get_entity_audit_logs`, `get_error_logs` |

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

---

## Local Setup

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in values
python scripts/seed_admin.py  # create first admin account
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
cp .env.example .env.local    # set VITE_API_URL and VITE_GOOGLE_CLIENT_ID
npm run dev                   # http://localhost:5173
```

---

## Environment Variables

### Railway (Backend)
```
SECRET_KEY=<min 32 chars: python -c "import secrets; print(secrets.token_hex(32))">
PEPPER=<min 32 chars: same as above>
MONGODB_URL=<Atlas connection string>
MONGODB_DB_NAME=parkash_book_depot
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://your-vercel-url.vercel.app"]
CLOUDINARY_CLOUD_NAME=<value>
CLOUDINARY_API_KEY=<value>
CLOUDINARY_API_SECRET=<value>
RESEND_API_KEY=<value>
EMAIL_FROM=noreply@yourdomain.com
GOOGLE_CLIENT_ID=<value>
GOOGLE_CLIENT_SECRET=<value>
```

### Vercel (Frontend)
```
VITE_API_URL=https://your-backend.railway.app/api/v1
VITE_GOOGLE_CLIENT_ID=<same as Railway GOOGLE_CLIENT_ID>
```

---

## Tests

```bash
cd backend
pytest tests/ -v
```

Covers: security utilities, state machine transitions, RBAC permissions.

---

*Built with FastAPI + React. Deployed on Railway + Vercel.*