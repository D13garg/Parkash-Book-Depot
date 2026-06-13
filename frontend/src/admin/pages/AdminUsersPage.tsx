import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { User } from "@/shared/types"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

async function fetchAllUsers(): Promise<User[]> {
  const res = await api.get<User[]>("/users")
  return res.data
}

function useAllUsers() {
  return useQuery({ queryKey: ["admin-users"], queryFn: fetchAllUsers })
}

function useToggleUserStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ userId, active }: { userId: string; active: boolean }) => {
      const action = active ? "reactivate" : "deactivate"
      const res = await api.patch<User>(`/users/${userId}/${action}`)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  })
}

const ROLE_COLORS: Record<string, string> = {
  admin: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  associate: "text-blue-400 bg-blue-400/10 border-blue-400/30",
  customer: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
}

export function AdminUsersPage() {
  const { data: users, isLoading, isError } = useAllUsers()
  const { mutate: toggleStatus, isPending: isToggling, variables: togglingVars } = useToggleUserStatus()

  const [search, setSearch] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")

  const filtered = (users ?? []).filter((u) => {
    const matchSearch = u.name.toLowerCase().includes(search.toLowerCase()) ||
                        u.email.toLowerCase().includes(search.toLowerCase())
    const matchRole   = roleFilter === "all" || u.role === roleFilter
    const matchStatus = statusFilter === "all" ||
                        (statusFilter === "active" ? u.is_active : !u.is_active)
    return matchSearch && matchRole && matchStatus
  })

  const counts = {
    total: users?.length ?? 0,
    active: users?.filter(u => u.is_active).length ?? 0,
    customers: users?.filter(u => u.role === "customer").length ?? 0,
    associates: users?.filter(u => u.role === "associate").length ?? 0,
  }

  if (isLoading) return <LoadingSpinner />
  if (isError) return <EmptyState title="Failed to load users" />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">User Management</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage customer and associate accounts</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Users", value: counts.total, icon: "👥" },
          { label: "Active",      value: counts.active, icon: "✅" },
          { label: "Customers",   value: counts.customers, icon: "🛍️" },
          { label: "Associates",  value: counts.associates, icon: "🔧" },
        ].map(({ label, value, icon }) => (
          <div key={label} className="bg-card border border-border rounded-xl p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <span>{icon}</span>{label}
            </div>
            <div className="text-2xl font-bold text-foreground">{value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="all">All roles</option>
          <option value="customer">Customer</option>
          <option value="associate">Associate</option>
          <option value="admin">Admin</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {/* Users table */}
      {filtered.length === 0 ? (
        <EmptyState title="No users found" description="Try adjusting your filters." />
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left px-4 py-3 text-muted-foreground font-medium">User</th>
                <th className="text-left px-4 py-3 text-muted-foreground font-medium">Role</th>
                <th className="text-left px-4 py-3 text-muted-foreground font-medium hidden md:table-cell">Joined</th>
                <th className="text-left px-4 py-3 text-muted-foreground font-medium">Status</th>
                <th className="text-right px-4 py-3 text-muted-foreground font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((user) => {
                const isThisToggling = isToggling && togglingVars?.userId === user.id
                return (
                  <tr key={user.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0">
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-foreground">{user.name}</div>
                          <div className="text-xs text-muted-foreground">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full border ${ROLE_COLORS[user.role] ?? ""}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">
                      {new Date(user.created_at).toLocaleDateString("en-IN", {
                        day: "numeric", month: "short", year: "numeric"
                      })}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full border ${
                        user.is_active
                          ? "text-success bg-success/10 border-success/30"
                          : "text-destructive bg-destructive/10 border-destructive/30"
                      }`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {/* Can't deactivate admin accounts */}
                      {user.role === "admin" ? (
                        <span className="text-xs text-muted-foreground">—</span>
                      ) : (
                        <button
                          onClick={() => toggleStatus({ userId: user.id, active: !user.is_active })}
                          disabled={isThisToggling}
                          className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors disabled:opacity-50 ${
                            user.is_active
                              ? "text-destructive border-destructive/40 hover:bg-destructive/10"
                              : "text-success border-success/40 hover:bg-success/10"
                          }`}
                        >
                          {isThisToggling
                            ? "..."
                            : user.is_active ? "Deactivate" : "Reactivate"}
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}