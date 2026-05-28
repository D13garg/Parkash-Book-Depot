import { Link } from "react-router-dom"

const BUSINESS_HOURS = [
  { day: "Monday", hours: "09:00 AM - 08:30 PM" },
  { day: "Tuesday", hours: "09:00 AM - 08:30 PM" },
  { day: "Wednesday", hours: "09:00 AM - 08:30 PM" },
  { day: "Thursday", hours: "09:00 AM - 08:30 PM" },
  { day: "Friday", hours: "09:00 AM - 08:30 PM" },
  { day: "Saturday", hours: "09:00 AM - 08:30 PM" },
  { day: "Sunday", hours: "11:00 AM - 03:00 PM" },
]

export function ContactUsPage() {
  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Contact Us
        </h2>

        <p className="text-sm text-muted-foreground mt-1">
          We're here to help. Reach out to us anytime.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-6">

        {/* Address */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">
            📍
          </div>

          <div>
            <p className="font-semibold text-foreground">
              Address
            </p>

            <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
              Parkash Book Depot <br />
              Railway Road <br />
              Jagraon
            </p>
          </div>
        </div>

        <hr className="border-border" />

        {/* Phone */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">
            📞
          </div>

          <div>
            <p className="font-semibold text-foreground">
              Phone
            </p>

            <a
              href="tel:+919876543210"
              className="text-sm text-primary hover:underline mt-1 block"
            >
              +91 98765 43210
            </a>
          </div>
        </div>

        <hr className="border-border" />

        {/* Email */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">
            ✉️
          </div>

          <div>
            <p className="font-semibold text-foreground">
              Email
            </p>

            <a
              href="mailto:parkashbookdepot723@gmail.com"
              className="text-sm text-primary hover:underline mt-1 block"
            >
              parkashbookdepot723@gmail.com
            </a>
          </div>
        </div>

        <hr className="border-border" />

        {/* Business Hours */}
        <div>
          <p className="font-semibold text-foreground">
            Business Hours
          </p>

          <div className="mt-3 space-y-2">
            {BUSINESS_HOURS.map((item) => (
              <div
                key={item.day}
                className="flex justify-between text-sm"
              >
                <span className="font-medium text-foreground">
                  {item.day}
                </span>

                <span className="text-muted-foreground">
                  {item.hours}
                </span>
              </div>
            ))}
          </div>
        </div>

        <hr className="border-border" />

        {/* Support */}
        <div className="pt-2">
          <Link
            to="/support"
            className="text-primary hover:underline"
          >
            Go to support page
          </Link>
        </div>

      </div>
    </div>
  )
}