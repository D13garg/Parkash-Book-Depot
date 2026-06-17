import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import api from "@/lib/axios"
import { useAuthStore } from "@/stores/authStore"
import type { TokenResponse } from "@/shared/types"

interface LoginData { email: string; password: string }
interface RegisterInitiateData { name: string; email: string; password: string; phone?: string }
interface OTPVerifyData { email: string; code: string }
interface ForgotPasswordInitiateData { email: string }
interface ForgotPasswordVerifyData { email: string; code: string; new_password: string }
interface GoogleAuthData { id_token: string }

const ROLE_HOME = { customer: "/customer", associate: "/associate", admin: "/admin" } as const

export function useAuth() {
  const navigate = useNavigate()
  const { setUser, clearAuth, user, isAuthenticated } = useAuthStore()

  const handleAuthSuccess = (data: TokenResponse) => {
    setUser(data.user)
    navigate(ROLE_HOME[data.user.role])
  }

  // ── Login ──────────────────────────────────────────────────────────────────
  const loginMutation = useMutation({
    mutationFn: async (data: LoginData) => {
      const res = await api.post<TokenResponse>("/auth/login", data)
      return res.data
    },
    onSuccess: handleAuthSuccess,
  })

  // ── Register step 1: send OTP ──────────────────────────────────────────────
  const registerInitiateMutation = useMutation({
    mutationFn: async (data: RegisterInitiateData) => {
      const res = await api.post<{ message: string; email: string }>("/auth/register/initiate", data)
      return res.data
    },
    onSuccess: (_data, variables) => {
      navigate("/verify-otp", { state: { email: variables.email, purpose: "register" } })
    },
  })

  // ── Register step 2: verify OTP → get tokens ──────────────────────────────
  const registerVerifyMutation = useMutation({
    mutationFn: async (data: OTPVerifyData) => {
      const res = await api.post<TokenResponse>("/auth/register/verify", data)
      return res.data
    },
    onSuccess: handleAuthSuccess,
  })

  // ── Forgot password step 1: send OTP ──────────────────────────────────────
  const forgotPasswordInitiateMutation = useMutation({
    mutationFn: async (data: ForgotPasswordInitiateData) => {
      const res = await api.post<{ message: string }>("/auth/forgot-password/initiate", data)
      return res.data
    },
    onSuccess: (_data, variables) => {
      navigate("/verify-otp", { state: { email: variables.email, purpose: "forgot_password" } })
    },
  })

  // ── Forgot password step 2: verify OTP + new password ─────────────────────
  const forgotPasswordVerifyMutation = useMutation({
    mutationFn: async (data: ForgotPasswordVerifyData) => {
      const res = await api.post<{ message: string }>("/auth/forgot-password/verify", data)
      return res.data
    },
    onSuccess: () => {
      navigate("/login", { state: { message: "Password reset successfully. Please sign in." } })
    },
  })

  // ── Google OAuth ───────────────────────────────────────────────────────────
  const googleAuthMutation = useMutation({
    mutationFn: async (data: GoogleAuthData) => {
      const res = await api.post<TokenResponse>("/auth/google", data)
      return res.data
    },
    onSuccess: handleAuthSuccess,
  })

  const logout = async () => {
    try {
      await api.post("/auth/logout")
    } catch {
      // Clear local state even if the server call fails
    } finally {
      clearAuth()
      navigate("/login")
    }
  }

  return {
    user,
    isAuthenticated: isAuthenticated(),
    login: loginMutation.mutate,
    loginError: loginMutation.error,
    isLoggingIn: loginMutation.isPending,
    registerInitiate: registerInitiateMutation.mutate,
    registerInitiateError: registerInitiateMutation.error,
    isRegisterInitiating: registerInitiateMutation.isPending,
    registerVerify: registerVerifyMutation.mutate,
    registerVerifyError: registerVerifyMutation.error,
    isRegisterVerifying: registerVerifyMutation.isPending,
    forgotPasswordInitiate: forgotPasswordInitiateMutation.mutate,
    forgotPasswordInitiateError: forgotPasswordInitiateMutation.error,
    isForgotPasswordInitiating: forgotPasswordInitiateMutation.isPending,
    forgotPasswordVerify: forgotPasswordVerifyMutation.mutate,
    forgotPasswordVerifyError: forgotPasswordVerifyMutation.error,
    isForgotPasswordVerifying: forgotPasswordVerifyMutation.isPending,
    googleAuth: googleAuthMutation.mutate,
    googleAuthError: googleAuthMutation.error,
    isGoogleAuthing: googleAuthMutation.isPending,
    logout,
  }
}
