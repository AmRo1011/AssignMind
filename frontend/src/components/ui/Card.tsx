/**
 * AssignMind — Card Component
 *
 * Container card with optional header, hover effect, and click handler.
 */

import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    hoverable?: boolean;
}

export function Card({ children, hoverable = false, className = "", ...props }: CardProps) {
    return (
        <div
            className={`rounded-2xl border border-border bg-surface p-5 shadow-sm ${hoverable ? "hover:shadow-md hover:border-primary/30 cursor-pointer transition-shadow" : ""} ${className}`}
            {...props}
        >
            {children}
        </div>
    );
}

interface CardHeaderProps {
    title: string;
    action?: ReactNode;
}

export function CardHeader({ title, action }: CardHeaderProps) {
    return (
        <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground font-[family-name:var(--font-outfit)]">
                {title}
            </h3>
            {action}
        </div>
    );
}
