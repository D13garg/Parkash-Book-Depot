import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User } from "@/shared/types"

interface AuthState {
  user: User | null
  sessionReady: boolean

  setUser: (user: User) => void
  setSessionReady: (ready: boolean) => void
  clearAuth: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      sessionReady: false,

      setUser: (user) => set({ user }),

      setSessionReady: (ready) => set({ sessionReady: ready }),

      clearAuth: () => set({ user: null }),

      isAuthenticated: () => !!get().user,
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ user: state.user }),
    }
  )
)
