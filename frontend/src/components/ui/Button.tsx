/**
 * AssignMind — Button Component
 *
 * Primary UI button with variants, sizes, and loading state.
 */

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Spinner } from "@/components/ui/Spinner";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    children: ReactNode;
}

const VARIANTS: Record<ButtonVariant, string> = {
    primary: "bg-primary text-white shadow-lg shadow-primary/25 hover:bg-primary-dark",
    secondary: "bg-surface border border-border text-foreground hover:bg-surface-hover",
    danger: "bg-error text-white hover:bg-red-600 shadow-lg shadow-error/25",
    ghost: "text-muted hover:text-foreground hover:bg-surface-hover",
};

const SIZES: Record<ButtonSize, string> = {
    sm: "px-3 py-1.5 text-sm rounded-lg",
    md: "px-5 py-2.5 text-sm rounded-xl",
    lg: "px-8 py-3 text-base rounded-xl",
};

export function Button({
    variant = "primary",
    size = "md",
    isLoading = false,
    disabled,
    children,
    className = "",
    ...props
}: ButtonProps) {
    return (
        <button
            disabled={disabled || isLoading}
            className={`inline-flex items-center justify-center font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
            {...props}
        >
            {isLoading && <Spinner size="sm" className="mr-2" />}
            {children}
        </button>
    );
}
