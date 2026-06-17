import { useEffect } from "react"
import api from "@/lib/axios"
import { useAuthStore } from "@/stores/authStore"
import type { User } from "@/shared/types"

/**
 * On app load, restore the session from httpOnly cookies via GET /auth/me.
 * The response echoes the CSRF token in X-CSRF-Token (cross-origin safe).
 */
export function AuthBootstrap() {
  const setUser = useAuthStore((s) => s.setUser)
  const setSessionReady = useAuthStore((s) => s.setSessionReady)
  const user = useAuthStore((s) => s.user)

  useEffect(() => {
    if (user) {
      setSessionReady(true)
      return
    }

    api
      .get<User>("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => {
        // No valid session — stay logged out
      })
      .finally(() => {
        setSessionReady(true)
      })
  }, [setUser, setSessionReady, user])

  return null
}
