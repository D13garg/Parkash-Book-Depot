import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import api from "@/lib/axios"
import { useAuthStore } from "@/stores/authStore"
import type { TokenResponse } from "@/shared/types"

interface LoginData {
  email: string
  password: string
}

interface RegisterData {
  name: string
  email: string
  password: string
  phone?: string
}

const ROLE_HOME = {
  customer:  "/customer",
  associate: "/associate",
  admin:     "/admin",
}

export function useAuth() {
  const navigate = useNavigate()
  const { setAuth, clearAuth, user, isAuthenticated } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: async (data: LoginData) => {
      const res = await api.post<TokenResponse>("/auth/login", data)
      return res.data
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token)
      navigate(ROLE_HOME[data.user.role])
    },
  })

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const res = await api.post<TokenResponse>("/auth/register", data)
      return res.data
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token)
      navigate(ROLE_HOME[data.user.role])
    },
  })

  const logout = () => {
    clearAuth()
    navigate("/login")
  }

  return {
    user,
    isAuthenticated: isAuthenticated(),
    login: loginMutation.mutate,
    loginError: loginMutation.error,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutate,
    registerError: registerMutation.error,
    isRegistering: registerMutation.isPending,
    logout,
  }
}
