import { useState } from "react"
import { useMyOrders } from "@/shared/hooks/useOrders"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { Pagination } from "@/shared/components/Pagination"

export function MyOrdersPage() {
  const [page, setPage] = useState(1)
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null)

  const { data, isLoading, isError } = useMyOrders(page, 10)

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading your orders..." />
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

  if (!data?.items || data.items.length === 0) {
    return (
      <EmptyState
        title="No orders yet"
        description="Browse books and place your first order."
        icon={<span className="text-4xl">📦</span>}
      />
    )
  }

  const toggleOrderDetails = (orderId: string) => {
    setExpandedOrderId(expandedOrderId === orderId ? null : orderId)
  }

  return (
    <div>
      <div className="page-header mb-8">
        <h2>My Orders</h2>
        <p>Manage and track your orders</p>
      </div>

      <div className="space-y-4">
        {data.items.map((order) => (
          <div
            key={order.id}
            className="surface-card border border-border rounded-lg overflow-hidden"
          >
            {/* Order Summary */}
            <button
              onClick={() => toggleOrderDetails(order.id)}
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
                    {formatDate(order.created_at)} at {formatTime(order.created_at)}
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Total Items</p>
                    <p className="font-semibold text-foreground">
                      {order.items.reduce((sum, item) => sum + item.quantity, 0)} items
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Total Amount</p>
                    <p className="text-lg font-bold text-primary">₹{order.total_amount.toFixed(2)}</p>
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
                  <h4 className="font-semibold text-foreground mb-3 text-sm">Order Items</h4>
                  <div className="space-y-2">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-background rounded-lg">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-foreground truncate">
                            {item.title}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            ₹{item.price.toFixed(2)} × {item.quantity} = ₹{item.subtotal.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Delivery Address */}
                <div>
                  <h4 className="font-semibold text-foreground mb-2 text-sm">Delivery Address</h4>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap bg-background p-2 rounded-lg">
                    {order.delivery_address}
                  </p>
                </div>

                {/* Contact Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Phone</p>
                    <p className="text-sm font-mono text-foreground">{order.phone}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Order Date</p>
                    <p className="text-sm text-foreground">
                      {formatDate(order.created_at)}
                    </p>
                  </div>
                </div>

                {/* Notes if present */}
                {order.notes && (
                  <div>
                    <h4 className="font-semibold text-foreground mb-2 text-sm">Notes</h4>
                    <p className="text-sm text-muted-foreground bg-background p-2 rounded-lg">
                      {order.notes}
                    </p>
                  </div>
                )}

                {/* Status Timeline */}
                <div>
                  <h4 className="font-semibold text-foreground mb-3 text-sm">Status</h4>
                  <div className="flex items-center gap-2 p-2 bg-background rounded-lg">
                    <span className="text-sm text-muted-foreground">Current Status:</span>
                    <StatusBadge status={order.status as any} />
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Last updated: {formatDate(order.updated_at)} at {formatTime(order.updated_at)}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="mt-8">
          <Pagination
            page={page}
            totalPages={data.total_pages}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  )
}
