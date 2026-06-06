import { useState } from "react"
import api from "../../lib/axios"

export default function ReviewPage() {
  const [submitted, setSubmitted] = useState(false)

  const [form, setForm] = useState({
    reviewer_name: "",
    reviewer_email: "",
    rating: 5,
    review_type: "overall",
    message: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await api.post("/reviews", form)
      setSubmitted(true)
    } catch (err) {
      console.error(err)
      alert("Failed to submit review")
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen mesh-bg flex items-center justify-center p-6">
        <div className="max-w-2xl w-full glass-panel rounded-2xl p-10 text-center shadow-card">
          <div className="text-5xl mb-4">✨</div>
          <h1 className="font-display text-3xl font-bold gradient-text mb-4">
            Thank you for your review!
          </h1>
          <p className="text-muted-foreground">
            Your feedback has been submitted successfully.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen mesh-bg py-10 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="glass-panel rounded-2xl p-8 shadow-card">
          <h1 className="font-display text-3xl font-bold gradient-text mb-2">
            Submit Project Review
          </h1>
          <p className="text-muted-foreground mb-8">
            Share feedback about the platform, frontend, backend, or architecture.
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block mb-2 text-sm font-medium text-foreground">Your Name</label>
              <input
                type="text"
                required
                className="input-field"
                value={form.reviewer_name}
                onChange={(e) => setForm({ ...form, reviewer_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-foreground">Email</label>
              <input
                type="email"
                required
                className="input-field"
                value={form.reviewer_email}
                onChange={(e) => setForm({ ...form, reviewer_email: e.target.value })}
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-foreground">Review Type</label>
              <select
                className="input-field"
                value={form.review_type}
                onChange={(e) => setForm({ ...form, review_type: e.target.value })}
              >
                <option value="overall">Overall</option>
                <option value="frontend">Frontend</option>
                <option value="backend">Backend</option>
                <option value="architecture">Architecture</option>
              </select>
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-foreground">Rating</label>
              <select
                className="input-field"
                value={form.rating}
                onChange={(e) => setForm({ ...form, rating: Number(e.target.value) })}
              >
                <option value={5}>5 — Excellent</option>
                <option value={4}>4 — Good</option>
                <option value={3}>3 — Average</option>
                <option value={2}>2 — Poor</option>
                <option value={1}>1 — Very Poor</option>
              </select>
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-foreground">Message</label>
              <textarea
                required
                rows={5}
                className="input-field resize-none"
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
              />
            </div>

            <button type="submit" className="w-full btn-primary py-3">
              Submit Review
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
