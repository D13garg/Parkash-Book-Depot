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

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
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
      <div className="max-w-2xl mx-auto p-10">
        <div className="bg-white border rounded-xl p-8 text-center shadow-sm">
          <h1 className="text-3xl font-bold mb-4">
            Thank you for your review!
          </h1>

          <p className="text-gray-600">
            Your feedback has been submitted successfully.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-10">
      <div className="bg-white border rounded-xl p-8 shadow-sm">
        <h1 className="text-3xl font-bold mb-2">
          Submit Project Review
        </h1>

        <p className="text-gray-500 mb-8">
          Share feedback about the platform,
          frontend, backend, or architecture.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >
          <div>
            <label className="block mb-2 font-medium">
              Your Name
            </label>

            <input
              type="text"
              required
              className="w-full border rounded-lg p-3"
              value={form.reviewer_name}
              onChange={(e) =>
                setForm({
                  ...form,
                  reviewer_name: e.target.value,
                })
              }
            />
          </div>

          <div>
            <label className="block mb-2 font-medium">
              Email
            </label>

            <input
              type="email"
              required
              className="w-full border rounded-lg p-3"
              value={form.reviewer_email}
              onChange={(e) =>
                setForm({
                  ...form,
                  reviewer_email: e.target.value,
                })
              }
            />
          </div>

          <div>
            <label className="block mb-2 font-medium">
              Review Type
            </label>

            <select
              className="w-full border rounded-lg p-3"
              value={form.review_type}
              onChange={(e) =>
                setForm({
                  ...form,
                  review_type: e.target.value,
                })
              }
            >
              <option value="overall">
                Overall
              </option>

              <option value="frontend">
                Frontend
              </option>

              <option value="backend">
                Backend
              </option>

              <option value="architecture">
                Architecture
              </option>
            </select>
          </div>

          <div>
            <label className="block mb-2 font-medium">
              Rating
            </label>

            <select
              className="w-full border rounded-lg p-3"
              value={form.rating}
              onChange={(e) =>
                setForm({
                  ...form,
                  rating: Number(e.target.value),
                })
              }
            >
              <option value={5}>5</option>
              <option value={4}>4</option>
              <option value={3}>3</option>
              <option value={2}>2</option>
              <option value={1}>1</option>
            </select>
          </div>

          <div>
            <label className="block mb-2 font-medium">
              Message
            </label>

            <textarea
              required
              rows={5}
              className="w-full border rounded-lg p-3"
              value={form.message}
              onChange={(e) =>
                setForm({
                  ...form,
                  message: e.target.value,
                })
              }
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Submit Review
          </button>
        </form>
      </div>
    </div>
  )
}