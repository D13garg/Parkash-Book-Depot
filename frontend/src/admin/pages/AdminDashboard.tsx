import { Routes, Route, Navigate } from "react-router-dom"
import { DashboardLayout }         from "@/shared/components/DashboardLayout"
import { RequestQueuePage }        from "./RequestQueuePage"
import { AllProjectsPage }         from "./AllProjectsPage"
import { AdminProjectDetailPage }  from "./AdminProjectDetailPage"
import { BookManagementPage }      from "./BookManagementPage"
import { AddBookPage }             from "./AddBookPage"
import { AdminReviewsPage }        from "./AdminReviewsPage"

const NAV_ITEMS = [
  { label: "Request Queue", path: "/admin/requests", icon: "📋" },
  { label: "All Projects",  path: "/admin/projects", icon: "📂" },
  { label: "Books",         path: "/admin/books",    icon: "📚" },
  { label: "Reviews",       path: "/admin/reviews",  icon: "⭐" },
  { label: "Profile",       path: "/admin/profile",  icon: "👤" },
]

export function AdminDashboard() {
  return (
    <DashboardLayout navItems={NAV_ITEMS} title="Admin Portal">
      <Routes>
        <Route index element={<Navigate to="requests" replace />} />
        <Route path="requests"            element={<RequestQueuePage />} />
        <Route path="projects"            element={<AllProjectsPage />} />
        <Route path="projects/:projectId" element={<AdminProjectDetailPage />} />
        <Route path="books"               element={<BookManagementPage />} />
        <Route path="books/add"           element={<AddBookPage />} />
        <Route path="reviews"             element={<AdminReviewsPage />} />
      </Routes>
    </DashboardLayout>
  )
}