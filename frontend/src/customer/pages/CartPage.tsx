import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useCartStore } from "@/stores/cartStore"
import { usePlaceOrder } from "@/shared/hooks/useOrders"
import { useAuthStore } from "@/stores/authStore"
import { EmptyState } from "@/shared/components/EmptyState"

export function CartPage() {
  const navigate = useNavigate()

  const {
    items,
    removeItem,
    updateQuantity,
    clearCart,
    totalPrice,
  } = useCartStore()

  const { user } = useAuthStore()

  const {
    mutate: placeOrder,
    isPending,
    error,
    isSuccess,
  } = usePlaceOrder()

  const [address, setAddress] = useState(user?.address ?? "")
  const [phone, setPhone] = useState(user?.phone ?? "")
  const [notes, setNotes] = useState("")
  const [showCheckout, setShowCheckout] = useState(false)

  const errorMessage = error
    ? (error as any)?.response?.data?.detail ??
      "Order failed. Please try again."
    : null

  const handlePlaceOrder = () => {
    if (!address.trim() || !phone.trim()) return

    placeOrder(
      {
        items: items.map((i) => ({
          book_id: i.book_id,
          quantity: i.quantity,
        })),
        delivery_address: address,
        phone,
        notes: notes || undefined,
      },
      {
        onSuccess: () => {
          clearCart()
          setTimeout(
            () => navigate("/customer/orders"),
            1500,
          )
        },
      },
    )
  }

  if (items.length === 0 && !isSuccess) {
    return (
      <EmptyState
        title="Your cart is empty"
        description="Browse books and add them to your cart."
        icon={<span className="text-4xl">🛒</span>}
        action={
          <button
            onClick={() => navigate("/customer/books")}
            className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
          >
            Browse Books
          </button>
        }
      />
    )
  }

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Your Cart
        </h2>

        <span className="text-sm text-muted-foreground">
          {items.length} item(s)
        </span>
      </div>

      {isSuccess && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700 text-sm">
          ✅ Order placed successfully! Redirecting to your
          orders...
        </div>
      )}

      {errorMessage && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-destructive/10 text-destructive text-sm">
          {errorMessage}
        </div>
      )}

      {/* Cart items */}
      <div className="bg-card border border-border rounded-xl overflow-hidden mb-4">
        {items.map((item, idx) => (
          <div
            key={item.book_id}
            className={`flex items-center gap-4 p-4 ${
              idx < items.length - 1
                ? "border-b border-border"
                : ""
            }`}
          >
            <div className="h-14 w-10 bg-muted rounded flex items-center justify-center text-xl flex-shrink-0">
              {item.cover_image_url ? (
                <img
                  src={item.cover_image_url}
                  alt={item.title}
                  className="h-full w-full object-cover rounded"
                />
              ) : (
                "📖"
              )}
            </div>

            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground text-sm line-clamp-1">
                {item.title}
              </p>

              <p className="text-sm text-primary font-semibold">
                ₹{item.price}
              </p>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() =>
                  updateQuantity(
                    item.book_id,
                    item.quantity - 1,
                  )
                }
                className="h-7 w-7 rounded-lg border border-border flex items-center justify-center hover:bg-muted text-sm transition-colors"
              >
                −
              </button>

              <span className="w-6 text-center text-sm font-medium">
                {item.quantity}
              </span>

              <button
                onClick={() =>
                  updateQuantity(
                    item.book_id,
                    item.quantity + 1,
                  )
                }
                disabled={item.quantity >= item.stock}
                className="h-7 w-7 rounded-lg border border-border flex items-center justify-center hover:bg-muted text-sm disabled:opacity-40 transition-colors"
              >
                +
              </button>
            </div>

            <div className="text-right flex-shrink-0">
              <p className="font-semibold text-sm">
                ₹
                {(item.price * item.quantity).toFixed(2)}
              </p>

              <button
                onClick={() =>
                  removeItem(item.book_id)
                }
                className="text-xs text-destructive hover:underline mt-0.5"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="flex items-center justify-between px-4 py-3 bg-muted rounded-xl mb-4">
        <span className="font-semibold text-foreground">
          Total
        </span>

        <span className="text-xl font-bold text-primary">
          ₹{totalPrice().toFixed(2)}
        </span>
      </div>

      {/* Checkout form */}
      {!showCheckout ? (
        <button
          onClick={() => setShowCheckout(true)}
          className="w-full py-3 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 transition-colors"
        >
          Proceed to Checkout
        </button>
      ) : (
        <div className="bg-card border border-border rounded-xl p-5 space-y-4">
          <h3 className="font-semibold text-foreground">
            Delivery Details
          </h3>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Delivery Address{" "}
              <span className="text-destructive">
                *
              </span>
            </label>

            <textarea
              value={address}
              onChange={(e) =>
                setAddress(e.target.value)
              }
              rows={3}
              placeholder="Full delivery address..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Phone{" "}
              <span className="text-destructive">
                *
              </span>
            </label>

            <input
              value={phone}
              onChange={(e) =>
                setPhone(e.target.value)
              }
              placeholder="+91 98765 43210"
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Notes{" "}
              <span className="text-muted-foreground font-normal">
                (optional)
              </span>
            </label>

            <input
              value={notes}
              onChange={(e) =>
                setNotes(e.target.value)
              }
              placeholder="Any special instructions..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <div className="flex gap-3 pt-1">
            <button
              onClick={handlePlaceOrder}
              disabled={
                isPending ||
                !address.trim() ||
                !phone.trim()
              }
              className="flex-1 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              {isPending
                ? "Placing Order..."
                : `Place Order — ₹${totalPrice().toFixed(
                    2,
                  )}`}
            </button>

            <button
              onClick={() =>
                setShowCheckout(false)
              }
              className="px-4 py-2.5 text-sm border border-border rounded-lg hover:bg-muted transition-colors"
            >
              Back
            </button>
          </div>
        </div>
      )}
    </div>
  )
}