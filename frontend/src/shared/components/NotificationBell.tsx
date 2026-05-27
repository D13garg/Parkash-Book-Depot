import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useNotifications, useMarkRead, useMarkAllRead, useUnreadCount } from "@/shared/hooks/useNotifications.ts"

const TYPE_ICONS: Record<string, string> = {
  request_submitted: "📋",
  review_submitted:  "⭐",
  project_assigned:  "📂",
}

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  const { data: notifications } = useNotifications()
  const { data: unreadCount = 0 } = useUnreadCount()
  const { mutate: markRead } = useMarkRead()
  const { mutate: markAllRead } = useMarkAllRead()

  const handleClick = (id: string, link: string | null, isRead: boolean) => {
    if (!isRead) markRead(id)
    if (link) {
      navigate(link)
      setOpen(false)
    }
  }

  return (
    <div className="relative">
      {/* Bell button */}
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
      >
        <span className="text-xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-5 w-5 rounded-full bg-destructive text-destructive-foreground text-xs font-bold flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />

          <div className="absolute right-0 top-11 z-50 w-80 bg-card border border-border rounded-xl shadow-xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <h3 className="font-semibold text-foreground text-sm">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllRead()}
                  className="text-xs text-primary hover:underline"
                >
                  Mark all read
                </button>
              )}
            </div>

            {/* List */}
            <div className="max-h-96 overflow-y-auto">
              {!notifications || notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No notifications yet
                </div>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => handleClick(n.id, n.link, n.is_read)}
                    className={`flex gap-3 px-4 py-3 cursor-pointer hover:bg-muted transition-colors border-b border-border last:border-0
                      ${!n.is_read ? "bg-primary/5" : ""}`}
                  >
                    <span className="text-lg flex-shrink-0 mt-0.5">
                      {TYPE_ICONS[n.type] ?? "🔔"}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm leading-snug ${!n.is_read ? "font-medium text-foreground" : "text-muted-foreground"}`}>
                        {n.message}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(n.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!n.is_read && (
                      <span className="flex-shrink-0 h-2 w-2 rounded-full bg-primary mt-2" />
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}