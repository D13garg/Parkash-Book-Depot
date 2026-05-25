import { RouterProvider } from "react-router-dom"
import { QueryProvider } from "@/providers/QueryProvider"
import { ToastContainer } from "@/shared/components/Toast"
import { router } from "@/router"

export default function App() {
  return (
    <QueryProvider>
      <RouterProvider router={router} />
      <ToastContainer />
    </QueryProvider>
  )
}
