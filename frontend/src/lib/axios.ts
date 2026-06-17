import axios from "axios"
import { useAuthStore } from "@/stores/authStore"

const apiHost = import.meta.env.VITE_API_URL || window.location.origin
const API_BASE_URL = `${apiHost}/api/v1`

/** In-memory CSRF token — synced from API response headers (cross-origin safe) */
let csrfToken: string | null = null

export function syncCsrfTokenFromResponse(headers: Record<string, unknown>): void {
  const token = headers["x-csrf-token"]
  if (typeof token === "string" && token) {
    csrfToken = token
  }
}

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase()
  if (method && method !== "GET" && method !== "HEAD" && method !== "OPTIONS") {
    if (csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    syncCsrfTokenFromResponse(response.headers as Record<string, unknown>)
    return response
  },

  async (error) => {
    const originalRequest = error.config

    if (error.response?.headers) {
      syncCsrfTokenFromResponse(error.response.headers as Record<string, unknown>)
    }

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      originalRequest._retry = true

      try {
        await api.post("/auth/refresh")
        return api(originalRequest)
      } catch {
        useAuthStore.getState().clearAuth()
        window.location.href = "/login"
      }
    }

    return Promise.reject(error)
  }
)

export default api
