import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface CartItem {
  book_id: string
  title: string
  price: number
  stock: number
  cover_image_url: string | null
  quantity: number
}

interface CartState {
  items: CartItem[]
  addItem: (item: Omit<CartItem, "quantity">) => void
  removeItem: (book_id: string) => void
  updateQuantity: (book_id: string, quantity: number) => void
  clearCart: () => void
  totalItems: () => number
  totalPrice: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) => {
        const existing = get().items.find((i) => i.book_id === item.book_id)
        if (existing) {
          set({ items: get().items.map((i) =>
            i.book_id === item.book_id
              ? { ...i, quantity: Math.min(i.quantity + 1, i.stock) }
              : i
          )})
        } else {
          set({ items: [...get().items, { ...item, quantity: 1 }] })
        }
      },

      removeItem: (book_id) =>
        set({ items: get().items.filter((i) => i.book_id !== book_id) }),

      updateQuantity: (book_id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(book_id)
        } else {
          set({ items: get().items.map((i) =>
            i.book_id === book_id
              ? { ...i, quantity: Math.min(quantity, i.stock) }
              : i
          )})
        }
      },

      clearCart: () => set({ items: [] }),
      totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),
      totalPrice: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }),
    { name: "cart-storage" }
  )
)
