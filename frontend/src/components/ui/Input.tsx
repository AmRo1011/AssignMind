/**
 * AssignMind — Input Component
 *
 * Styled text input with label, error state, and helper text.
 */

import { forwardRef, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, helperText, id, className = "", ...props }, ref) => {
        const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

        return (
            <div className="flex flex-col gap-1.5">
                {label && (
                    <label htmlFor={inputId} className="text-sm font-medium text-foreground">
                        {label}
                    </label>
                )}
                <input
                    id={inputId}
                    ref={ref}
                    className={`w-full rounded-xl border bg-surface px-4 py-2.5 text-sm text-foreground placeholder:text-muted transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed ${error ? "border-error" : "border-border"} ${className}`}
                    aria-describedby={error ? `${inputId}-error` : undefined}
                    aria-invalid={!!error}
                    {...props}
                />
                {error && (
                    <p id={`${inputId}-error`} className="text-xs text-error" role="alert">
                        {error}
                    </p>
                )}
                {helperText && !error && (
                    <p className="text-xs text-muted">{helperText}</p>
                )}
            </div>
        );
    }
);

Input.displayName = "Input";
