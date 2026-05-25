import { Routes, Route, Navigate } from "react-router-dom"
import { DashboardLayout } from "@/shared/components/DashboardLayout"
import { AssignedProjectsPage } from "./AssignedProjectsPage"
import { ProjectDetailPage }    from "./ProjectDetailPage"
import { AddUpdatePage }        from "./AddUpdatePage"
import { ProfilePage }          from "@/customer/pages/ProfilePage"

const NAV_ITEMS = [
  { label: "My Projects", path: "/associate/projects", icon: "📂" },
  { label: "Profile",     path: "/associate/profile",  icon: "👤" },
]

export function AssociateDashboard() {
  return (
    <DashboardLayout navItems={NAV_ITEMS} title="Associate Portal">
      <Routes>
        <Route index element={<Navigate to="projects" replace />} />
        <Route path="projects"                      element={<AssignedProjectsPage />} />
        <Route path="projects/:projectId"           element={<ProjectDetailPage />} />
        <Route path="projects/:projectId/add-update" element={<AddUpdatePage />} />
        <Route path="profile"                        element={<ProfilePage />} />
      </Routes>
    </DashboardLayout>
  )
}
