import { create } from "zustand"
type ToastType = "success" | "error" | "info" | "warning"

interface Toast {
  id: string
  type: ToastType
  message: string
}

interface ToastStore {
  toasts: Toast[]
  add: (type: ToastType, message: string) => void
  remove: (id: string) => void
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  add: (type, message) => {
    const id = Math.random().toString(36).slice(2)
    set((state) => ({ toasts: [...state.toasts, { id, type, message }] }))
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
    }, 4000)
  },
  remove: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}))

export function useToast() {
  const { add } = useToastStore()
  return {
    success: (msg: string) => add("success", msg),
    error: (msg: string) => add("error", msg),
    info: (msg: string) => add("info", msg),
    warning: (msg: string) => add("warning", msg),
  }
}

const TOAST_STYLES: Record<ToastType, string> = {
  success: "alert-success border",
  error: "alert-error border",
  info: "bg-info-muted text-info border border-info/25",
  warning: "alert-warning border",
}

const TOAST_ICONS: Record<ToastType, string> = {
  success: "✅",
  error: "❌",
  info: "ℹ️",
  warning: "⚠️",
}

export function ToastContainer() {
  const { toasts, remove } = useToastStore()

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            flex items-start gap-3 px-4 py-3 rounded-xl shadow-card
            pointer-events-auto cursor-pointer backdrop-blur-xl
            animate-in slide-in-from-right-5 fade-in duration-300
            ${TOAST_STYLES[toast.type]}
          `}
          onClick={() => remove(toast.id)}
        >
          <span className="text-base flex-shrink-0 mt-0.5">{TOAST_ICONS[toast.type]}</span>
          <p className="text-sm font-medium leading-snug">{toast.message}</p>
        </div>
      ))}
    </div>
  )
}
