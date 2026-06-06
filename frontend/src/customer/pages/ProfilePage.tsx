import { useAuthStore } from "@/stores/authStore"

export function ProfilePage() {
  const { user } = useAuthStore()

  if (!user) return null

  return (
    <div className="max-w-xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">My Profile</h2>
        <p className="text-sm text-muted-foreground mt-1">Your account information</p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-5">

        {/* Avatar */}
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold text-primary">
            {user.name[0].toUpperCase()}
          </div>
          <div>
            <p className="text-lg font-semibold text-foreground">{user.name}</p>
            <p className="text-sm text-muted-foreground capitalize">{user.role}</p>
          </div>
        </div>

        <hr className="border-border" />

        {/* Details */}
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Email
            </label>
            <p className="mt-1 text-sm text-foreground">{user.email}</p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Phone
            </label>
            <p className="mt-1 text-sm text-foreground">
              {user.phone ?? "Not provided"}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Address
            </label>
            <p className="mt-1 text-sm text-foreground">
              {user.address ?? "Not provided"}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Member Since
            </label>
            <p className="mt-1 text-sm text-foreground">
              {new Date(user.created_at).toLocaleDateString("en-IN", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Account Status
            </label>
            <p className="mt-1">
              <span className="inline-flex items-center gap-1.5 text-sm text-success">
                <span className="h-2 w-2 rounded-full bg-success shadow-glow" />
                Active
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
