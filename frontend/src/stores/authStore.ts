import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User } from "@/shared/types"

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  clearAuth: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),

      clearAuth: () =>
        set({ user: null, accessToken: null, refreshToken: null }),

      isAuthenticated: () => !!get().accessToken && !!get().user,
    }),
    {
      name: "auth-storage",   // key in localStorage — matches what axios.ts reads
    }
  )
)
