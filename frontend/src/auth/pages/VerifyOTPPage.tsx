import { useState, useRef, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "@/shared/hooks/useAuth"

function getApiError(error: unknown): string | null {
  if (!error) return null
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) return detail.map((e: { msg?: string }) => e.msg).filter(Boolean).join(". ")
  return "Something went wrong. Please try again."
}

export function VerifyOTPPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { email, purpose } = (location.state ?? {}) as { email?: string; purpose?: string }

  // Redirect away if landed here without proper state
  useEffect(() => {
    if (!email || !purpose) navigate("/register", { replace: true })
  }, [email, purpose, navigate])

  const {
    registerVerify, registerVerifyError, isRegisterVerifying,
    forgotPasswordVerify, forgotPasswordVerifyError, isForgotPasswordVerifying,
  } = useAuth()

  // 4 individual digit inputs for better UX
  const [digits, setDigits] = useState(["", "", "", ""])
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordError, setPasswordError] = useState<string | null>(null)

  const isForgot = purpose === "forgot_password"
  const isLoading = isRegisterVerifying || isForgotPasswordVerifying
  const apiError = getApiError(isForgot ? forgotPasswordVerifyError : registerVerifyError)

  const code = digits.join("")

  const handleDigitChange = (index: number, value: string) => {
    // Only accept digits
    const digit = value.replace(/\D/g, "").slice(-1)
    const next = [...digits]
    next[index] = digit
    setDigits(next)
    // Auto-advance
    if (digit && index < 3) inputRefs.current[index + 1]?.focus()
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 4)
    const next = [...digits]
    pasted.split("").forEach((d, i) => { next[i] = d })
    setDigits(next)
    const lastFilled = Math.min(pasted.length, 3)
    inputRefs.current[lastFilled]?.focus()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (code.length !== 4) return

    if (isForgot) {
      setPasswordError(null)
      if (!newPassword) { setPasswordError("New password is required."); return }
      if (newPassword !== confirmPassword) { setPasswordError("Passwords do not match."); return }
      forgotPasswordVerify({ email: email!, code, new_password: newPassword })
    } else {
      registerVerify({ email: email!, code })
    }
  }

  if (!email || !purpose) return null

  return (
    <div className="min-h-screen mesh-bg flex items-center justify-center px-4 relative overflow-hidden">
      <div className="glow-orb w-96 h-96 bg-primary/20 -top-48 left-1/2 -translate-x-1/2" />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div
            className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 border border-primary/30 text-3xl shadow-glow-lg mb-5"
            style={{ animation: "float 4s ease-in-out infinite" }}
          >
            {isForgot ? "🔑" : "✉️"}
          </div>
          <h1 className="font-display text-3xl font-bold gradient-text">
            {isForgot ? "Reset Password" : "Verify Email"}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            We sent a 4-digit code to{" "}
            <span className="text-foreground font-medium">{email}</span>
          </p>
          <p className="text-xs text-muted-foreground mt-1">Code expires in 3 minutes</p>
        </div>

        <div className="glass-panel rounded-2xl p-8 shadow-card">
          {apiError && <div className="mb-5 alert-error">{apiError}</div>}
          {passwordError && <div className="mb-5 alert-error">{passwordError}</div>}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 4-digit OTP input */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-3 text-center">
                Enter verification code
              </label>
              <div className="flex gap-3 justify-center" onPaste={handlePaste}>
                {digits.map((d, i) => (
                  <input
                    key={i}
                    ref={(el) => { inputRefs.current[i] = el }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={d}
                    onChange={(e) => handleDigitChange(i, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(i, e)}
                    className="w-14 h-14 text-center text-2xl font-bold rounded-xl border-2 border-input bg-background text-foreground focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/30 transition-all"
                  />
                ))}
              </div>
            </div>

            {/* Password fields for forgot password flow */}
            {isForgot && (
              <>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">New Password</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Confirm Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat new password"
                    className="input-field"
                  />
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={isLoading || code.length !== 4}
              className="w-full btn-primary disabled:opacity-50"
            >
              {isLoading
                ? (isForgot ? "Resetting..." : "Verifying...")
                : (isForgot ? "Reset Password" : "Verify & Create Account")}
            </button>
          </form>

          <div className="mt-5 text-center space-y-2">
            <p className="text-sm text-muted-foreground">
              Didn't receive it?{" "}
              <button
                type="button"
                onClick={() => navigate(isForgot ? "/forgot-password" : "/register")}
                className="text-primary font-semibold hover:underline"
              >
                Go back and resend
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}