import { useState } from "react"
import { useAdminOrders, useUpdateOrderStatus } from "@/shared/hooks/useOrders"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { Pagination } from "@/shared/components/Pagination"
import type { Order } from "@/shared/hooks/useOrders"

const ORDER_STATUSES = [
  "pending",
  "confirmed",
  "processing",
  "shipped",
  "delivered",
  "cancelled",
]

export function AdminOrdersPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null)
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [updatingStatus, setUpdatingStatus] = useState<{
    orderId: string
    newStatus: string
  } | null>(null)

  const { data, isLoading, isError } = useAdminOrders(
    page,
    10,
    statusFilter || undefined
  )
  const { mutate: updateOrderStatus, isPending: isUpdatingStatus } =
    useUpdateOrderStatus()

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const handleStatusChange = (orderId: string, newStatus: string) => {
    setUpdatingStatus({ orderId, newStatus })
  }

  const confirmStatusChange = (orderId: string, newStatus: string) => {
    updateOrderStatus(
      { orderId, status: newStatus },
      {
        onSuccess: () => {
          setUpdatingStatus(null)
        },
      }
    )
  }

  const filteredOrders = data?.items.filter((order) => {
    if (!dateFrom && !dateTo) return true

    const orderDate = new Date(order.created_at).getTime()
    if (dateFrom) {
      const fromDate = new Date(dateFrom).getTime()
      if (orderDate < fromDate) return false
    }
    if (dateTo) {
      const toDate = new Date(dateTo)
      toDate.setHours(23, 59, 59, 999)
      if (orderDate > toDate.getTime()) return false
    }
    return true
  }) || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading orders..." />
      </div>
    )
  }

  if (isError) {
    return (
      <EmptyState
        title="Failed to load orders"
        description="Something went wrong. Please try again."
        icon={<span className="text-4xl">⚠️</span>}
      />
    )
  }

  return (
    <div>
      <div className="page-header mb-8">
        <h2>Order Management</h2>
        <p>Monitor and manage all customer orders</p>
      </div>

      {/* Filters */}
      <div className="surface-card p-4 rounded-lg mb-6 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Filter by Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="input-field"
            >
              <option value="">All statuses</option>
              {ORDER_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Date From
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value)
                setPage(1)
              }}
              className="input-field"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-foreground block mb-2">
              Date To
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value)
                setPage(1)
              }}
              className="input-field"
            />
          </div>
        </div>

        {(statusFilter || dateFrom || dateTo) && (
          <button
            onClick={() => {
              setStatusFilter("")
              setDateFrom("")
              setDateTo("")
              setPage(1)
            }}
            className="text-sm text-primary hover:text-primary/80 transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Orders List */}
      {filteredOrders.length === 0 ? (
        <EmptyState
          title="No orders found"
          description={
            statusFilter || dateFrom || dateTo
              ? "Try adjusting your filters."
              : "No orders yet."
          }
          icon={<span className="text-4xl">📦</span>}
        />
      ) : (
        <div className="space-y-4">
          {filteredOrders.map((order) => (
            <div
              key={order.id}
              className="surface-card border border-border rounded-lg overflow-hidden"
            >
              {/* Order Summary */}
              <button
                onClick={() =>
                  setExpandedOrderId(
                    expandedOrderId === order.id ? null : order.id
                  )
                }
                className="w-full p-4 hover:bg-muted/50 transition-colors text-left"
              >
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <div className="flex-1 min-w-48">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-semibold text-muted-foreground">
                        Order #{order.id.slice(0, 8).toUpperCase()}
                      </span>
                      <StatusBadge status={order.status as any} />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Customer: {order.customer_name}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatDate(order.created_at)} at {formatTime(order.created_at)}
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Items</p>
                      <p className="font-semibold text-foreground">
                        {order.items.reduce((sum, item) => sum + item.quantity, 0)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Total</p>
                      <p className="text-lg font-bold text-primary">
                        ₹{order.total_amount.toFixed(2)}
                      </p>
                    </div>
                    <div className="text-muted-foreground">
                      {expandedOrderId === order.id ? "▼" : "▶"}
                    </div>
                  </div>
                </div>
              </button>

              {/* Order Details */}
              {expandedOrderId === order.id && (
                <div className="border-t border-border p-4 space-y-4 bg-muted/30">
                  {/* Items */}
                  <div>
                    <h4 className="font-semibold text-foreground mb-3 text-sm">
                      Order Items
                    </h4>
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-background rounded-lg"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground truncate">
                              {item.title}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              ₹{item.price.toFixed(2)} × {item.quantity} = ₹
                              {item.subtotal.toFixed(2)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Delivery Info */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-foreground mb-2 text-sm">
                        Delivery Address
                      </h4>
                      <p className="text-sm text-muted-foreground bg-background p-2 rounded-lg whitespace-pre-wrap">
                        {order.delivery_address}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground mb-2 text-sm">
                        Contact
                      </h4>
                      <p className="text-sm font-mono text-foreground bg-background p-2 rounded-lg">
                        {order.phone}
                      </p>
                    </div>
                  </div>

                  {/* Notes if present */}
                  {order.notes && (
                    <div>
                      <h4 className="font-semibold text-foreground mb-2 text-sm">
                        Customer Notes
                      </h4>
                      <p className="text-sm text-muted-foreground bg-background p-2 rounded-lg">
                        {order.notes}
                      </p>
                    </div>
                  )}

                  {/* Status Update */}
                  <div>
                    <h4 className="font-semibold text-foreground mb-3 text-sm">
                      Update Status
                    </h4>
                    {updatingStatus?.orderId === order.id ? (
                      <div className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          Change status to{" "}
                          <span className="font-semibold">
                            {updatingStatus.newStatus}
                          </span>
                          ?
                        </p>
                        <div className="flex gap-2">
                          <button
                            onClick={() =>
                              confirmStatusChange(order.id, updatingStatus.newStatus)
                            }
                            disabled={isUpdatingStatus}
                            className="flex-1 btn-primary text-sm disabled:opacity-50"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setUpdatingStatus(null)}
                            disabled={isUpdatingStatus}
                            className="flex-1 btn-secondary text-sm disabled:opacity-50"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <select
                        value={order.status}
                        onChange={(e) =>
                          handleStatusChange(order.id, e.target.value)
                        }
                        className="input-field"
                      >
                        {ORDER_STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {status.charAt(0).toUpperCase() + status.slice(1)}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="mt-8">
          <Pagination
            currentPage={page}
            totalPages={data.pages}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  )
}
