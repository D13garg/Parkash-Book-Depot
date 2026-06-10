# Parkash Book Depot — Full Stack Platform

A production-grade bookstore management system combining inventory management, customer project requests, internal operations, and full observability.
---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| State | Zustand, TanStack Query v5 |
| Backend | Python, FastAPI, Pydantic |
| Database | MongoDB (Motor async driver) |
| Auth | JWT (access + refresh tokens), bcrypt + pepper |
| Storage | Cloudinary (gallery images) |
| Deploy | Vercel (frontend), Railway (backend) |

---

## Project Structure

```
Parkash-Book-Depot/
├── docker-compose.yml
├── backend/
│   ├── main.py                          # uvicorn entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── scripts/
│   │   ├── seed_admin.py               # create first admin account
│   │   └── create_associates.py        # create associate accounts
│   ├── tests/
│   │   └── unit/
│   │       ├── test_security.py
│   │       ├── test_state_machines.py
│   │       └── test_permissions.py
│   └── app/
│       ├── main.py                      # FastAPI app factory
│       ├── core/
│       │   ├── config.py               # settings + env vars
│       │   ├── database.py             # MongoDB connection
│       │   ├── security.py             # JWT, bcrypt + pepper
│       │   ├── enums.py                # roles, statuses, state machines
│       │   ├── exceptions.py           # custom HTTP exceptions
│       │   ├── email_validation.py     # Level A email validation
│       │   └── create_indexes.py       # MongoDB indexes + TTL
│       ├── models/                      # MongoDB document shapes
│       │   ├── user.py
│       │   ├── book.py
│       │   ├── order.py
│       │   ├── project_request.py
│       │   ├── project.py
│       │   ├── project_update.py
│       │   ├── review.py
│       │   ├── gallery.py
│       │   ├── notification.py
│       │   ├── audit_log.py
│       │   ├── error_log.py
│       │   └── metrics.py
│       ├── schemas/                     # API request/response shapes
│       │   ├── user.py
│       │   ├── book.py
│       │   ├── order.py
│       │   ├── project_request.py
│       │   ├── project.py
│       │   ├── review.py
│       │   ├── gallery.py
│       │   ├── notification.py
│       │   ├── audit_log.py
│       │   ├── error_log.py
│       │   ├── metrics.py
│       │   └── analytics.py
│       ├── repositories/                # MongoDB queries only
│       │   ├── user_repository.py
│       │   ├── book_repository.py
│       │   ├── order_repository.py
│       │   ├── project_request_repository.py
│       │   ├── project_repository.py
│       │   ├── project_update_repository.py
│       │   ├── review_repository.py
│       │   ├── gallery_repository.py
│       │   ├── notification_repository.py
│       │   ├── audit_log_repository.py
│       │   ├── error_log_repository.py
│       │   └── metrics_repository.py
│       ├── services/                    # business logic
│       │   ├── auth_service.py
│       │   ├── book_service.py
│       │   ├── order_service.py
│       │   ├── project_request_service.py
│       │   ├── project_service.py
│       │   ├── review_service.py
│       │   ├── gallery_service.py
│       │   ├── notification_service.py
│       │   ├── audit_log_service.py
│       │   ├── error_log_service.py
│       │   ├── metrics_service.py
│       │   └── analytics_service.py
│       ├── permissions/                 # RBAC + ownership guards
│       │   ├── role_permissions.py
│       │   ├── project_permissions.py
│       │   └── project_request_permissions.py
│       ├── dependencies/
│       │   ├── database.py             # get_db()
│       │   └── auth.py                 # get_current_user, role guards
│       ├── middleware/
│       │   ├── logging.py
│       │   ├── security_headers.py
│       │   ├── rate_limit.py
│       │   └── error_handler.py
│       └── api/v1/
│           ├── router.py               # all routers registered here
│           └── endpoints/
│               ├── health.py
│               ├── auth.py
│               ├── users.py
│               ├── books.py
│               ├── orders.py
│               ├── project_requests.py
│               ├── projects.py
│               ├── reviews.py
│               ├── gallery.py
│               ├── notifications.py
│               ├── audit_logs.py
│               ├── error_logs.py
│               ├── metrics.py
│               └── analytics.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── vercel.json
    ├── Dockerfile
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── auth/pages/
        │   ├── LoginPage.tsx
        │   └── RegisterPage.tsx
        ├── customer/pages/
        │   ├── CustomerDashboard.tsx
        │   ├── BooksPage.tsx
        │   ├── CartPage.tsx
        │   ├── MyOrdersPage.tsx
        │   ├── MyRequestsPage.tsx
        │   ├── SubmitRequestPage.tsx
        │   ├── MyReviewPage.tsx
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
        │   ├── AdminProjectDetailPage.tsx
        │   ├── AdminOrdersPage.tsx
        │   ├── BookManagementPage.tsx
        │   ├── AddBookPage.tsx
        │   ├── AdminReviewsPage.tsx
        │   ├── AdminGalleryPage.tsx
        │   ├── AdminAuditLogsPage.tsx
        │   ├── AdminErrorLogsPage.tsx
        │   ├── AdminMetricsDashboard.tsx
        │   └── AdminAnalyticsPage.tsx
        ├── shared/
        │   ├── components/
        │   │   ├── DashboardLayout.tsx
        │   │   ├── BookDetailPanel.tsx
        │   │   ├── CartIcon.tsx
        │   │   ├── NotificationBell.tsx
        │   │   ├── StatusBadge.tsx
        │   │   ├── Pagination.tsx
        │   │   ├── LoadingSpinner.tsx
        │   │   ├── EmptyState.tsx
        │   │   ├── Skeletons.tsx
        │   │   └── Toast.tsx
        │   ├── hooks/
        │   │   ├── useAuth.ts
        │   │   ├── useBooks.ts
        │   │   ├── useOrders.ts
        │   │   ├── useProjectRequests.ts
        │   │   ├── useProjects.ts
        │   │   ├── useReviews.ts
        │   │   ├── useGallery.ts
        │   │   ├── useNotifications.ts
        │   │   ├── useAdminRequests.ts
        │   │   ├── useAdminProjects.ts
        │   │   ├── useAdminBooks.ts
        │   │   ├── useAuditLogs.ts
        │   │   ├── useErrorLogs.ts
        │   │   ├── useMetrics.ts
        │   │   └── useAnalytics.ts
        │   └── types/
        │       └── index.ts
        ├── stores/
        │   ├── authStore.ts
        │   └── cartStore.ts
        ├── providers/
        │   └── QueryProvider.tsx
        └── router/
            ├── index.tsx
            └── ProtectedRoute.tsx
```

---

## User Roles

| Role | Access |
|------|--------|
| **Customer** | Browse books, submit requests, track requests, write reviews, view gallery |
| **Associate** | View assigned projects, add progress updates, change project status |
| **Admin** | Full access — manage everything, view all dashboards |

---

## API Endpoints

| Module | Prefix | Endpoints |
|--------|--------|-----------|
| Auth | `/api/v1/auth` | register, login, refresh, me |
| Users | `/api/v1/users` | associates list |
| Books | `/api/v1/books` | CRUD, stock management, low-stock || Orders | `/api/v1/orders` | place, my orders, all orders (admin), status update || Project Requests | `/api/v1/project-requests` | submit, list, status update |
| Projects | `/api/v1/projects` | create, assign, status, updates timeline |
| Reviews | `/api/v1/reviews` | submit, my reviews, all reviews (admin) |
| Gallery | `/api/v1/gallery` | upload, caption, delete |
| Notifications | `/api/v1/notifications` | list, mark read, unread count |
| Audit Logs | `/api/v1/audit-logs` | list with filters, by entity |
| Error Logs | `/api/v1/error-logs` | list with filters (7-day TTL) |
| Metrics | `/api/v1/metrics` | summary, 30-day trend |
| Analytics | `/api/v1/analytics` | full operational analytics |

---

## Order Management

**Customer Features:**
- Browse books with detailed view drawer panel
- Add books to cart (Zustand-based state management)
- Checkout with delivery address & notes
- View order history with status tracking
- Track real-time delivery status

**Admin Features:**
- View all customer orders with pagination
- Filter orders by status and date range
- Update order status through state machine
- Approve/reject orders based on stock availability
- Audit trail of all order modifications

**Order Statuses:**
- `pending` → New order created
- `confirmed` → Order approved
- `processing` → Being packed/prepared
- `shipped` → In transit
- `delivered` → Order received
- `cancelled` → Cancelled by customer or admin

---

## Security Features

- **JWT** access + refresh tokens
- **bcrypt + pepper** password hashing
- **Rate limiting** on auth endpoints (slowapi)
- **Security headers** middleware (X-Frame-Options, HSTS, CSP)
- **Request size limiting** (5MB max)
- **Email validation** — blocks disposable/fake emails
- **Password strength** — uppercase, lowercase, number, special char required
- **RBAC + ownership** checks on every sensitive endpoint
- **Docs disabled** in production (`ENVIRONMENT=production`)
- **State machines** enforce valid workflow transitions

---

## Observability

| Layer | Collection | Retention |
|-------|-----------|-----------|
| Audit Logs | `audit_logs` | Permanent |
| Error Logs | `error_logs` | 7 days (MongoDB TTL) |
| Metrics | `metrics_hourly` | Permanent |
| Analytics | Aggregated on-demand | No storage |

---

## MongoDB Collections

```
users               project_requests    projects
project_updates     books               orders
reviews             gallery             notifications
audit_logs          error_logs          metrics_hourly
```

---

## State Machines

**Project Request Flow:**
```
submitted → under_review → accepted → converted_to_project
                        → rejected
```

**Project Flow:**
```
pending → assigned → in_progress → waiting_supplier → completed
       → cancelled (from any state)
```

**Order Flow:**
```
pending → confirmed → processing → shipped → delivered
       → cancelled (from any state before delivered)
```

---

## Local Setup

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in values
python scripts/seed_admin.py  # create admin account
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
npm run dev                   # http://localhost:5173

# 3. Docker (everything at once)
docker-compose up --build
```

---

## Environment Variables (Railway)

```
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
PEPPER=<generate: python -c "import secrets; print(secrets.token_hex(32))">
MONGODB_URL=<your Atlas connection string>
MONGODB_DB_NAME=parkash_book_depot
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://your-vercel-url.vercel.app"]
CLOUDINARY_CLOUD_NAME=<your value>
CLOUDINARY_API_KEY=<your value>
CLOUDINARY_API_SECRET=<your value>
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
*CI/CD pipeline implemented.*
