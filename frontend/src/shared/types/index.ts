// ── Enums (mirror backend enums.py) ──────────────────────────────────────────

export type UserRole = "customer" | "associate" | "admin"

export type ProjectRequestStatus =
  | "submitted"
  | "under_review"
  | "accepted"
  | "rejected"
  | "converted_to_project"

export type ProjectStatus =
  | "pending"
  | "assigned"
  | "in_progress"
  | "waiting_supplier"
  | "completed"
  | "cancelled"

// ── User ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  is_active: boolean
  phone: string | null
  address: string | null
  created_at: string
  updated_at: string
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
}

// ── Books ─────────────────────────────────────────────────────────────────────

export interface Book {
  id: string
  title: string
  authors: string[]
  categories: string[]
  price: number
  stock: number
  is_low_stock: boolean
  publisher: string | null
  isbn: string | null
  description: string | null
  cover_image_url: string | null
  edition: string | null
  language: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ── Project Requests ──────────────────────────────────────────────────────────

export interface ProjectRequest {
  id: string
  customer_id: string
  title: string
  description: string
  category: string
  requirements: string | null
  quantity: number | null
  institution_name: string | null
  institution_address: string | null
  contact_phone: string | null
  status: ProjectRequestStatus
  admin_notes: string | null
  rejection_reason: string | null
  created_at: string
  updated_at: string
}

// ── Projects ──────────────────────────────────────────────────────────────────

export interface Project {
  id: string
  request_id: string
  created_by: string
  assigned_to: string | null
  title: string
  description: string
  priority: string
  deadline: string | null
  status: ProjectStatus
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ProjectUpdate {
  id: string
  project_id: string
  updated_by: string
  message: string
  status_changed_to: ProjectStatus | null
  attachments: string[]
  created_at: string
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
// ── Reviews ───────────────────────────────────────────────────────────────────

export interface Review {
  id: string
  customer_id: string
  customer_name: string
  rating: number
  category: string
  message: string
  created_at: string
}
// ── Notifications ─────────────────────────────────────────────────────────────

export interface Notification {
  id: string
  user_id: string
  type: string
  message: string
  link: string | null
  is_read: boolean
  created_at: string
}
// ── Gallery ───────────────────────────────────────────────────────────────────

export interface GalleryItem {
  id: string
  image_url: string
  public_id: string
  caption: string | null
  uploaded_by: string
  uploaded_by_name: string
  created_at: string
}