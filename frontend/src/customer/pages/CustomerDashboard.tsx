import { Routes, Route, Navigate } from "react-router-dom"
import { DashboardLayout }   from "@/shared/components/DashboardLayout"
import { BooksPage }         from "./BooksPage"
import { MyRequestsPage }    from "./MyRequestsPage"
import { SubmitRequestPage } from "./SubmitRequestPage"
import { ProfilePage }       from "./ProfilePage"
import { MyReviewsPage }     from "./MyReviewPage"
import { SubmitReviewPage }  from "./SubmitReviewPage"
import { ContactUsPage }     from "./ContactUsPage"
import { GalleryPage }       from "./GalleryPage.tsx"

const NAV_ITEMS = [
  { label: "Browse Books",   path: "/customer/books",          icon: "📚" },
  { label: "My Requests",    path: "/customer/requests",       icon: "📋" },
  { label: "Submit Request", path: "/customer/submit-request", icon: "➕" },
  { label: "My Reviews",     path: "/customer/reviews",        icon: "⭐" },
  { label: "Project Gallery",path: "/customer/gallery",        icon: "🖼️" },
  { label: "Contact Us",     path: "/customer/contact",        icon: "📞" },
  { label: "Profile",        path: "/customer/profile",        icon: "👤" },
]

export function CustomerDashboard() {
  return (
    <DashboardLayout navItems={NAV_ITEMS} title="Customer Portal">
      <Routes>
        <Route index element={<Navigate to="books" replace />} />
        <Route path="books"          element={<BooksPage />} />
        <Route path="requests"       element={<MyRequestsPage />} />
        <Route path="submit-request" element={<SubmitRequestPage />} />
        <Route path="reviews"        element={<MyReviewsPage />} />
        <Route path="submit-review"  element={<SubmitReviewPage />} />
        <Route path="gallery"        element={<GalleryPage />} />
        <Route path="contact"        element={<ContactUsPage />} />
        <Route path="profile"        element={<ProfilePage />} />
      </Routes>
    </DashboardLayout>
  )
}