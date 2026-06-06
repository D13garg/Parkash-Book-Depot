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
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="relative">
        <div
          className={`${sizes[size]} animate-spin rounded-full border-[3px] border-muted border-t-primary`}
        />
        <div
          className={`absolute inset-0 ${sizes[size]} rounded-full border-[3px] border-transparent border-t-primary/30 animate-spin`}
          style={{ animationDirection: "reverse", animationDuration: "1.5s" }}
        />
      </div>
      {text && <p className="text-sm text-muted-foreground font-medium">{text}</p>}
    </div>
  )
}
