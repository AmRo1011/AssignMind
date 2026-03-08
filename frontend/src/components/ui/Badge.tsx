/**
 * AssignMind — Badge Component
 *
 * Small status indicator with color variants.
 */

import type { ReactNode } from "react";

type BadgeVariant = "default" | "success" | "warning" | "error" | "info" | "primary";

interface BadgeProps {
    variant?: BadgeVariant;
    children: ReactNode;
    className?: string;
}

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
    default: "bg-border/50 text-muted",
    success: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    warning: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
    error: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
    info: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    primary: "bg-primary/10 text-primary",
};

export function Badge({ variant = "default", children, className = "" }: BadgeProps) {
    return (
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${VARIANT_CLASSES[variant]} ${className}`}>
            {children}
        </span>
    );
}
