import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link } from "react-router-dom"
import { useAuth } from "@/shared/hooks/useAuth"

const registerSchema = z.object({
  name:     z.string().min(2, "Name must be at least 2 characters"),
  email:    z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  phone:    z.string().optional(),
})

type RegisterForm = z.infer<typeof registerSchema>

function getApiError(error: unknown): string | null {
  if (!error) return null
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) return detail.map((e: { msg?: string }) => e.msg).filter(Boolean).join(". ")
  return "Registration failed. Please try again."
}

export function RegisterPage() {
  const { registerInitiate, registerInitiateError, isRegisterInitiating } = useAuth()

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = (data: RegisterForm) => registerInitiate(data)
  const errorMessage = getApiError(registerInitiateError)

  return (
    <div className="min-h-screen mesh-bg flex items-center justify-center px-4 py-10 relative overflow-hidden">
      <div className="glow-orb w-96 h-96 bg-primary/20 -top-48 left-1/2 -translate-x-1/2" />
      <div className="glow-orb w-64 h-64 bg-purple/10 bottom-0 left-0" style={{ animationDelay: "2s" }} />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 border border-primary/30 text-3xl shadow-glow-lg mb-5" style={{ animation: "float 4s ease-in-out infinite" }}>
            📚
          </div>
          <h1 className="font-display text-3xl font-bold gradient-text">Parkash Book Depot</h1>
          <p className="mt-2 text-sm text-muted-foreground">Create your account</p>
        </div>

        <div className="glass-panel rounded-2xl p-8 shadow-card">
          {errorMessage && <div className="mb-5 alert-error">{errorMessage}</div>}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Full Name</label>
              <input {...register("name")} type="text" placeholder="Your full name" className="input-field" />
              {errors.name && <p className="mt-1 text-xs text-destructive">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <input {...register("email")} type="email" placeholder="you@example.com" className="input-field" />
              {errors.email && <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Password</label>
              <input {...register("password")} type="password" placeholder="Min. 8 characters" className="input-field" />
              {errors.password && <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Phone <span className="text-muted-foreground font-normal">(optional)</span>
              </label>
              <input {...register("phone")} type="tel" placeholder="+91 98765 43210" className="input-field" />
            </div>

            <button type="submit" disabled={isRegisterInitiating} className="w-full btn-primary">
              {isRegisterInitiating ? "Sending code..." : "Continue"}
            </button>
          </form>

          <p className="mt-4 text-xs text-center text-muted-foreground">
            A 4-digit verification code will be sent to your email.
          </p>

          <p className="mt-4 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link to="/login" className="text-primary font-semibold hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}