import { useState } from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { useAuthStore } from "@/stores/authStore"
import { NotificationBell } from "./NotificationBell"
import type { ReactNode } from "react"

interface NavItem {
  label: string
  path: string
  icon: string
}

interface DashboardLayoutProps {
  children: ReactNode
  navItems: NavItem[]
  title: string
}

export function DashboardLayout({ children, navItems, title }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate("/login")
  }

  return (
    <div className="min-h-screen mesh-bg flex">

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-border transform transition-transform duration-300 ease-out ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:relative lg:translate-x-0 lg:flex lg:flex-col`}>
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent pointer-events-none" />

        <div className="relative flex items-center gap-3 px-6 py-6 border-b border-border">
          <div className="h-10 w-10 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center text-xl shadow-glow">
            📚
          </div>
          <div>
            <span className="font-display font-bold text-foreground text-sm leading-tight tracking-tight">Parkash</span>
            <span className="block font-display font-bold text-primary text-xs tracking-widest uppercase">Book Depot</span>
          </div>
        </div>

        <nav className="relative flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
                 ${isActive
                   ? "nav-active-glow"
                   : "text-muted-foreground hover:bg-muted/60 hover:text-foreground hover:translate-x-0.5"}`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="relative px-4 py-5 border-t border-border">
          <div className="flex items-center gap-3 mb-3 p-2 rounded-lg bg-muted/40">
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary/30 to-primary/10 border border-primary/30 flex items-center justify-center text-sm font-bold text-primary shadow-glow">
              {user?.name?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground truncate">{user?.name}</p>
              <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
          >
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-4 px-6 py-4 glass-panel border-b border-border">
          <div className="flex items-center gap-4">
            <button
              className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors"
              onClick={() => setSidebarOpen(true)}
            >
              ☰
            </button>
            <div>
              <h1 className="font-display text-lg font-bold text-foreground tracking-tight">{title}</h1>
              <p className="text-xs text-muted-foreground hidden sm:block">Welcome back, {user?.name?.split(" ")[0]}</p>
            </div>
          </div>
          <NotificationBell />
        </header>

        <main className="flex-1 p-6 page-enter">
          {children}
        </main>
      </div>
    </div>
  )
}
