import { createBrowserRouter, Navigate } from "react-router-dom"
import { ProtectedRoute } from "./ProtectedRoute"

import { LoginPage }    from "@/auth/pages/LoginPage"
import { RegisterPage } from "@/auth/pages/RegisterPage"
import ReviewPage from "@/public/pages/ReviewPage"
import { CustomerDashboard }  from "@/customer/pages/CustomerDashboard"
import { AssociateDashboard } from "@/associate/pages/AssociateDashboard"
import { AdminDashboard }     from "@/admin/pages/AdminDashboard"

export const router = createBrowserRouter([
  // ── Public ──────────────────────────────────────────────────────────────
  { path: "/login",    element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/review", element: <ReviewPage /> },

  // ── Customer ─────────────────────────────────────────────────────────────
  {
    path: "/customer/*",
    element: (
      <ProtectedRoute allowedRoles={["customer"]}>
        <CustomerDashboard />
      </ProtectedRoute>
    ),
  },

  // ── Associate ─────────────────────────────────────────────────────────────
  {
    path: "/associate/*",
    element: (
      <ProtectedRoute allowedRoles={["associate"]}>
        <AssociateDashboard />
      </ProtectedRoute>
    ),
  },

  // ── Admin ─────────────────────────────────────────────────────────────────
  {
    path: "/admin/*",
    element: (
      <ProtectedRoute allowedRoles={["admin"]}>
        <AdminDashboard />
      </ProtectedRoute>
    ),
  },

  // ── Redirects ─────────────────────────────────────────────────────────────
  { path: "/",  element: <Navigate to="/login" replace /> },
  { path: "*",  element: <Navigate to="/login" replace /> },
])
