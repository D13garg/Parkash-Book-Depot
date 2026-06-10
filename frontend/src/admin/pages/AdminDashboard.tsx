import { Routes, Route, Navigate } from "react-router-dom"
import { DashboardLayout }         from "@/shared/components/DashboardLayout"
import { RequestQueuePage }        from "./RequestQueuePage"
import { AllProjectsPage }         from "./AllProjectsPage"
import { AdminProjectDetailPage }  from "./AdminProjectDetailPage"
import { BookManagementPage }      from "./BookManagementPage"
import { AddBookPage }             from "./AddBookPage"
import { EditBookPage }            from "./EditBookPage"
import { AdminOrdersPage }         from "./AdminOrdersPage"
import { AdminReviewsPage }        from "./AdminReviewsPage"
import { AdminGalleryPage }        from "./AdminGalleryPage"
import { AdminAuditLogsPage }     from "./AdminAuditLogsPage"
import { AdminErrorLogsPage }     from "./AdminErrorLogsPage"
import { AdminMetricsDashboard }  from "./AdminMetricsDashboard"
import { AdminAnalyticsPage }     from "./AdminAnalyticsPage"

const NAV_ITEMS = [
  { label: "Request Queue", path: "/admin/requests", icon: "📋" },
  { label: "All Projects",  path: "/admin/projects", icon: "📂" },
  { label: "Orders",        path: "/admin/orders",   icon: "📦" },
  { label: "Books",         path: "/admin/books",    icon: "📚" },
  { label: "Reviews",       path: "/admin/reviews",  icon: "⭐" },
  { label: "Gallery",       path: "/admin/gallery",  icon: "🖼️" },
  { label: "Activity Logs", path: "/admin/audit-logs",  icon: "📋" },
  { label: "Error Logs",     path: "/admin/error-logs",  icon: "🔴" },
  { label: "Metrics",       path: "/admin/metrics",     icon: "📊" },
  { label: "Analytics",     path: "/admin/analytics",   icon: "🧠" },
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
        <Route path="orders"              element={<AdminOrdersPage />} />
        <Route path="books"               element={<BookManagementPage />} />
        <Route path="books/add"           element={<AddBookPage />} />
        <Route path="books/:bookId/edit"  element={<EditBookPage />} />
        <Route path="reviews"             element={<AdminReviewsPage />} />
        <Route path="gallery"             element={<AdminGalleryPage />} />
        <Route path="audit-logs"         element={<AdminAuditLogsPage />} />
        <Route path="error-logs"          element={<AdminErrorLogsPage />} />
        <Route path="metrics"             element={<AdminMetricsDashboard />} />
        <Route path="analytics"           element={<AdminAnalyticsPage />} />
      </Routes>
    </DashboardLayout>
  )
}