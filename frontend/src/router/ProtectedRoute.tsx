import { Navigate } from "react-router-dom"
import { useAuthStore } from "@/stores/authStore"
import type { UserRole } from "@/shared/types"
import type { ReactNode } from "react"

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles?: UserRole[]
}

const ROLE_HOME: Record<UserRole, string> = {
  customer:  "/customer",
  associate: "/associate",
  admin:     "/admin",
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, isAuthenticated, sessionReady } = useAuthStore()

  if (!sessionReady) {
    return null
  }

  if (!isAuthenticated() || !user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={ROLE_HOME[user.role]} replace />
  }

  return <>{children}</>
}
