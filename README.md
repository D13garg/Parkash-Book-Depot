# 📚 Parkash Book Depot

A full-stack project management platform for Parkash Book Depot, enabling customers to submit project requests, associates to manage and update assigned projects, and admins to oversee the entire workflow — all through a clean, role-based interface.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS |
| **State Management** | Zustand, TanStack Query (React Query v5) |
| **Forms & Validation** | React Hook Form, Zod |
| **Backend** | FastAPI (Python), Uvicorn |
| **Primary Database** | MongoDB (via Motor — async driver) |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **HTTP Client** | Axios |
| **Routing** | React Router v7 |

---

## 📁 Project Structure

```
Parkash-Book-Depot/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers (auth, books, projects, requests)
│   │   ├── core/               # Config, DB connection, enums, security
│   │   ├── dependencies/       # FastAPI dependency injection (auth, DB)
│   │   ├── middleware/         # Logging middleware
│   │   ├── models/             # MongoDB document models
│   │   ├── permissions/        # Role-based access control logic
│   │   ├── repositories/       # DB query layer
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Business logic layer
│   ├── scripts/
│   │   ├── seed_admin.py       # Create initial admin account
│   │   └── create_associates.py
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py
│
└── frontend/
    └── src/
        ├── admin/              # Admin pages & components
        ├── associate/          # Associate pages & components
        ├── customer/           # Customer pages & components
        ├── auth/               # Login & Register pages
        ├── shared/
        │   ├── hooks/          # Reusable React Query hooks
        │   ├── components/     # Shared UI components
        │   └── types/          # Shared TypeScript types
        ├── stores/             # Zustand auth store
        └── router/             # Route definitions & ProtectedRoute
```

---

## 👥 User Roles

| Role | Capabilities |
|---|---|
| **Customer** | Register, submit project requests, track request status, browse books, manage profile |
| **Associate** | View assigned projects, post project updates, manage workflow stages |
| **Admin** | Manage all users, review & approve/reject requests, convert to projects, manage book catalog |

### Project Request Lifecycle

```
SUBMITTED → UNDER_REVIEW → ACCEPTED → CONVERTED_TO_PROJECT
                         ↘ REJECTED
```

### Project Status Lifecycle

```
PENDING → ASSIGNED → IN_PROGRESS → COMPLETED
                   ↘            ↘ WAITING_SUPPLIER → IN_PROGRESS
    (any stage)  → CANCELLED
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB running locally or a MongoDB Atlas URI

---

### 1. Clone the Repository

```bash
git clone https://github.com/D13garg/Parkash-Book-Depot.git
cd Parkash-Book-Depot
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MongoDB URI, SECRET_KEY, etc.

# Seed the admin account
python scripts/seed_admin.py

# Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.development .env.development.local
# Set VITE_API_URL=http://localhost:8000

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing secret — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `MONGODB_URL` | MongoDB connection URI (local or Atlas) |
| `MONGODB_DB_NAME` | Database name (default: `parkash_book_depot`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token TTL (default: 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token TTL (default: 3) |
| `ALLOWED_ORIGINS` | Comma-separated allowed CORS origins |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Used by `seed_admin.py` script |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

---

## 🛠️ Available Scripts

### Backend

| Command | Description |
|---|---|
| `uvicorn main:app --reload` | Start dev server with hot reload |
| `python scripts/seed_admin.py` | Create the first admin user |
| `python scripts/create_associates.py` | Create associate accounts |
| `pytest` | Run backend tests |

### Frontend

| Command | Description |
|---|---|
| `npm run dev` | Start Vite dev server |
| `npm run build` | TypeScript compile + production build |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build locally |

---

## 📡 API Endpoints

All endpoints are prefixed with `/api/v1`.

| Module | Base Path | Description |
|---|---|---|
| Health | `/health` | API health check |
| Auth | `/auth` | Register, login, refresh token |
| Books | `/books` | Book catalog (CRUD for admins) |
| Project Requests | `/project-requests` | Submit and manage requests |
| Projects | `/projects` | Project lifecycle management |

Full interactive documentation is available at `/docs` when the backend is running.

---

## 🔒 Security Notes

- Passwords are hashed using **bcrypt** via `passlib`
- Authentication uses **JWT access + refresh tokens**
- All protected routes use FastAPI dependency injection for role enforcement
- CORS is restricted to configured `ALLOWED_ORIGINS`
- Sensitive environment variables must never be committed to version control

---

## 🗺️ Roadmap

- [x] Phase 1–5: Core auth, project requests, project management, book catalog, admin dashboard
- [ ] Phase 6: Orders & payments (PostgreSQL integration — schema ready)
- [ ] Phase 7: Notifications system
- [ ] Phase 8: Analytics dashboard

---

## 📄 License

This project is private and maintained by the Parkash Book Depot team.
