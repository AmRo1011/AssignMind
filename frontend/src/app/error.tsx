"use client";

/**
 * AssignMind — Global Error Page
 */

interface ErrorProps {
    error: Error & { digest?: string };
    reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-background text-center px-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-500 mb-6">
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            </div>
            <h2 className="text-2xl font-semibold text-foreground">
                Something went wrong
            </h2>
            <p className="mt-2 max-w-md text-muted-foreground">
                An unexpected error occurred. Please try again.
            </p>
            <button
                onClick={reset}
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5"
            >
                Try Again
            </button>
        </div>
    );
}
