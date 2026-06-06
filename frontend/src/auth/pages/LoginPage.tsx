import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link } from "react-router-dom"
import { useAuth } from "@/shared/hooks/useAuth"

const loginSchema = z.object({
  email:    z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
})

type LoginForm = z.infer<typeof loginSchema>

export function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })

  const onSubmit = (data: LoginForm) => login(data)

  const apiDetail = (loginError as { response?: { data?: { detail?: unknown } } })
    ?.response?.data?.detail

  const errorMessage = loginError
    ? typeof apiDetail === "string"
      ? apiDetail
      : Array.isArray(apiDetail)
        ? apiDetail.map((e: { msg?: string }) => e.msg).filter(Boolean).join(". ")
        : "Login failed. Please try again."
    : null

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
          {errorMessage && (
            <div className="mb-5 alert-error">
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <input
                {...register("email")}
                type="email"
                placeholder="you@example.com"
                className="input-field"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Password</label>
              <input
                {...register("password")}
                type="password"
                placeholder="••••••••"
                className="input-field"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full btn-primary"
            >
              {isLoggingIn ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link to="/register" className="text-primary font-semibold hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
