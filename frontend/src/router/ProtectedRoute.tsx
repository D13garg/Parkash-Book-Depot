import { Navigate } from "react-router-dom"
import { useAuthStore } from "@/stores/authStore"
import type { UserRole } from "@/shared/types"
import type { ReactNode } from "react"

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles?: UserRole[]
}

// Role → default dashboard mapping
const ROLE_HOME: Record<UserRole, string> = {
  customer:  "/customer",
  associate: "/associate",
  admin:     "/admin",
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, accessToken } = useAuthStore()

  // 1. Not logged in — redirect to login
  if (!accessToken || !user) {
    return <Navigate to="/login" replace />
  }

  // 2. Logged in but wrong role — redirect to their correct dashboard
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={ROLE_HOME[user.role]} replace />
  }

  return <>{children}</>
}
