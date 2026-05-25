import axios from "axios"

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
})

// ── Request interceptor — attach access token to every request ────────────────
api.interceptors.request.use((config) => {
  const raw = localStorage.getItem("auth-storage")
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      const token = parsed?.state?.accessToken
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch {
      // malformed storage — ignore
    }
  }
  return config
})

// ── Response interceptor — handle 401 by attempting token refresh ─────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only attempt refresh once to avoid infinite loops
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const raw = localStorage.getItem("auth-storage")
        if (!raw) throw new Error("No auth storage")

        const parsed = JSON.parse(raw)
        const refreshToken = parsed?.state?.refreshToken
        if (!refreshToken) throw new Error("No refresh token")

        // Call refresh endpoint directly (no interceptor loop)
        const { data } = await axios.post("/api/v1/auth/refresh", {
          refresh_token: refreshToken,
        })

        // Update the access token in localStorage
        parsed.state.accessToken = data.access_token
        localStorage.setItem("auth-storage", JSON.stringify(parsed))

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch {
        // Refresh failed — clear storage and redirect to login
        localStorage.removeItem("auth-storage")
        window.location.href = "/login"
      }
    }

    return Promise.reject(error)
  }
)

export default api
