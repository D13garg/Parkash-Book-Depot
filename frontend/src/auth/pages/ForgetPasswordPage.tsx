import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link } from "react-router-dom"
import { useAuth } from "@/shared/hooks/useAuth"

const schema = z.object({
  email: z.string().email("Enter a valid email"),
})
type FormData = z.infer<typeof schema>

function getApiError(error: unknown): string | null {
  if (!error) return null
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === "string") return detail
  return "Something went wrong. Please try again."
}

export function ForgotPasswordPage() {
  const { forgotPasswordInitiate, forgotPasswordInitiateError, isForgotPasswordInitiating } = useAuth()

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormData) => forgotPasswordInitiate(data)
  const apiError = getApiError(forgotPasswordInitiateError)

  return (
    <div className="min-h-screen mesh-bg flex items-center justify-center px-4 relative overflow-hidden">
      <div className="glow-orb w-96 h-96 bg-primary/20 -top-48 left-1/2 -translate-x-1/2" />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div
            className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 border border-primary/30 text-3xl shadow-glow-lg mb-5"
            style={{ animation: "float 4s ease-in-out infinite" }}
          >
            🔑
          </div>
          <h1 className="font-display text-3xl font-bold gradient-text">Forgot Password</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your email and we'll send a verification code
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-8 shadow-card">
          {apiError && <div className="mb-5 alert-error">{apiError}</div>}

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

            <button
              type="submit"
              disabled={isForgotPasswordInitiating}
              className="w-full btn-primary"
            >
              {isForgotPasswordInitiating ? "Sending code..." : "Send verification code"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Remembered it?{" "}
            <Link to="/login" className="text-primary font-semibold hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}