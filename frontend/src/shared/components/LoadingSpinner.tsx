interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  text?: string
}

const sizes = {
  sm: "h-4 w-4",
  md: "h-8 w-8",
  lg: "h-12 w-12",
}

export function LoadingSpinner({ size = "md", text }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizes[size]} animate-spin rounded-full border-4 border-muted border-t-primary`}
      />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}
