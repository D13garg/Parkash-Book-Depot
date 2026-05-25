import { Routes, Route, Navigate } from "react-router-dom"
import { DashboardLayout } from "@/shared/components/DashboardLayout"
import { BooksPage } from "./BooksPage"
import { MyRequestsPage } from "./MyRequestsPage"
import { SubmitRequestPage } from "./SubmitRequestPage"
import { ProfilePage } from "./ProfilePage"

const NAV_ITEMS = [
  { label: "Browse Books",   path: "/customer/books",          icon: "📚" },
  { label: "My Requests",    path: "/customer/requests",       icon: "📋" },
  { label: "Submit Request", path: "/customer/submit-request", icon: "➕" },
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
        <Route path="profile"        element={<ProfilePage />} />
      </Routes>
    </DashboardLayout>
  )
}
