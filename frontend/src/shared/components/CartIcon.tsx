import { useNavigate } from "react-router-dom"
import { useCartStore } from "@/stores/cartStore"

export function CartIcon() {
  const navigate = useNavigate()
  const totalItems = useCartStore((s) => s.totalItems())

  return (
    <button
      onClick={() => navigate("/customer/cart")}
      className="relative p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
    >
      <span className="text-xl">🛒</span>

      {totalItems > 0 && (
        <span className="absolute -top-0.5 -right-0.5 h-5 w-5 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
          {totalItems > 9 ? "9+" : totalItems}
        </span>
      )}
    </button>
  )
}