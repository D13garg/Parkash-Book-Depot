import { Link } from "react-router-dom"

const BUSINESS_HOURS = [
  { day: "Monday", hours: "09:00 AM - 06:00 PM" },
  { day: "Tuesday", hours: "09:00 AM - 06:00 PM" },
  { day: "Wednesday", hours: "09:00 AM - 06:00 PM" },
  { day: "Thursday", hours: "09:00 AM - 06:00 PM" },
  { day: "Friday", hours: "09:00 AM - 06:00 PM" },
  { day: "Saturday", hours: "10:00 AM - 04:00 PM" },
  { day: "Sunday", hours: "Closed" },
]

export function ContactUsPage() {
  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Contact Us</h2>
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
            <p className="font-semibold text-foreground">Address</p>
            <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
              Parkash Book Depot<br />
              Railway Road<br />
              Jagraon
            </p>
          </div>
        </div>

        <hr className="border-border" />

        {/* Contact details */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">📞</div>
          <div>
            <p className="font-semibold text-foreground">Phone</p>
            <p className="text-sm text-muted-foreground mt-1">+91 98765 43210</p>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">✉️</div>
          <div>
            <p className="font-semibold text-foreground">Email</p>
            <p className="text-sm text-muted-foreground mt-1">support@parkash-book-depot.local</p>
          </div>
        </div>

        {/* Business hours */}
        <div>
          <p className="font-semibold text-foreground">Business Hours</p>
          <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
            {BUSINESS_HOURS.map((h) => (
              <div key={h.day} className="flex justify-between">
                <span className="font-medium text-foreground">{h.day}</span>
                <span>{h.hours}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Support link */}
        <div className="pt-4">
          <Link to="/support" className="text-primary underline">
            Go to support page
          </Link>
        </div>

      </div>
    </div>
  )
}

        {/* Email */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">
            ✉️
          </div>
          <div>
            <p className="font-semibold text-foreground">Email</p>
            
              href="mailto:parkashbookdepot723@gmail.com"
              className="text-sm text-primary hover:underline mt-1 block"
            >
              parkashbookdepot723@gmail.com
            </a>
          </div>
        </div>

        <hr className="border-border" />

        {/* Hours */}
        <div className="flex gap-4">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl flex-shrink-0">
            🕐
          </div>
          <div>
            <p className="font-semibold text-foreground">Business Hours</p>
            <div className="mt-1 space-y-1 text-sm text-muted-foreground">
              <p>Monday – Saturday: 9:00 AM – 8:30 PM</p>
              <p>Sunday: 11:00 AM – 3:00 PM</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}