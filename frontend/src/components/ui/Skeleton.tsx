/**
 * AssignMind — Skeleton Loading Components
 *
 * Reusable shimmer placeholders for content loading states.
 */

interface SkeletonProps {
    className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
    return (
        <div
            className={`animate-pulse rounded-lg bg-muted/60 ${className}`}
        />
    );
}

export function CardSkeleton() {
    return (
        <div className="rounded-2xl border border-border bg-surface p-5 space-y-3">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-full" />
        </div>
    );
}

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-2/3" />
                        <Skeleton className="h-3 w-1/3" />
                    </div>
                </div>
            ))}
        </div>
    );
}

export function KanbanSkeleton() {
    return (
        <div className="grid grid-cols-3 gap-6">
            {[0, 1, 2].map((col) => (
                <div key={col} className="space-y-3">
                    <Skeleton className="h-8 w-32" />
                    <CardSkeleton />
                    <CardSkeleton />
                    {col === 0 && <CardSkeleton />}
                </div>
            ))}
        </div>
    );
}

export function ChatSkeleton() {
    return (
        <div className="space-y-4 p-4">
            {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className={`flex gap-3 ${i % 2 === 0 ? "" : "flex-row-reverse"}`}>
                    <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
                    <div className="space-y-1 max-w-[60%]">
                        <Skeleton className="h-3 w-20" />
                        <Skeleton className={`h-16 ${i % 2 === 0 ? "w-64" : "w-48"} rounded-xl`} />
                    </div>
                </div>
            ))}
        </div>
    );
}
