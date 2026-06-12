import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link, useLocation } from "react-router-dom"
import { useEffect, useRef } from "react"
import { useAuth } from "@/shared/hooks/useAuth"

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (res: { credential: string }) => void }) => void
          renderButton: (el: HTMLElement, config: object) => void
        }
      }
    }
  }
}

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string

const loginSchema = z.object({
  email:    z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
})
type LoginForm = z.infer<typeof loginSchema>

function getApiError(error: unknown): string | null {
  if (!error) return null
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) return detail.map((e: { msg?: string }) => e.msg).filter(Boolean).join(". ")
  return "Login failed. Please try again."
}

export function LoginPage() {
  const { login, isLoggingIn, loginError, googleAuth, isGoogleAuthing, googleAuthError } = useAuth()
  const location = useLocation()
  const googleBtnRef = useRef<HTMLDivElement>(null)

  const successMessage = (location.state as { message?: string })?.message

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginForm) => login(data)
  const errorMessage = getApiError(loginError) ?? getApiError(googleAuthError)

  // Load Google Identity Services script and render button
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return

    const initGoogle = () => {
      window.google?.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (res) => googleAuth({ id_token: res.credential }),
      })
      if (googleBtnRef.current) {
        window.google?.accounts.id.renderButton(googleBtnRef.current, {
          theme: "filled_black",
          size: "large",
          width: 400,
          text: "signin_with",
          shape: "rectangular",
        })
      }
    }

    if (window.google) {
      initGoogle()
    } else {
      const script = document.createElement("script")
      script.src = "https://accounts.google.com/gsi/client"
      script.async = true
      script.defer = true
      script.onload = initGoogle
      document.body.appendChild(script)
    }
  }, [googleAuth])

  return (
    <div className="min-h-screen mesh-bg flex items-center justify-center px-4 relative overflow-hidden">
      <div className="glow-orb w-96 h-96 bg-primary/20 -top-48 left-1/2 -translate-x-1/2" />
      <div className="glow-orb w-64 h-64 bg-info/10 bottom-0 right-0" style={{ animationDelay: "3s" }} />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 border border-primary/30 text-3xl shadow-glow-lg mb-5" style={{ animation: "float 4s ease-in-out infinite" }}>
            📚
          </div>
          <h1 className="font-display text-3xl font-bold gradient-text">Parkash Book Depot</h1>
          <p className="mt-2 text-sm text-muted-foreground">Sign in to your account</p>
        </div>

        <div className="glass-panel rounded-2xl p-8 shadow-card">
          {successMessage && (
            <div className="mb-5 px-4 py-3 rounded-lg bg-success/10 border border-success/30 text-success text-sm">
              {successMessage}
            </div>
          )}
          {errorMessage && <div className="mb-5 alert-error">{errorMessage}</div>}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <input {...register("email")} type="email" placeholder="you@example.com" className="input-field" />
              {errors.email && <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-medium text-foreground">Password</label>
                <Link to="/forgot-password" className="text-xs text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <input {...register("password")} type="password" placeholder="••••••••" className="input-field" />
              {errors.password && <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={isLoggingIn || isGoogleAuthing} className="w-full btn-primary">
              {isLoggingIn ? "Signing in..." : "Sign in"}
            </button>
          </form>

          {/* Google Sign In */}
          {GOOGLE_CLIENT_ID && (
            <>
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">or</span>
                </div>
              </div>
              <div ref={googleBtnRef} className="flex justify-center" />
            </>
          )}

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link to="/register" className="text-primary font-semibold hover:underline">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  )
}