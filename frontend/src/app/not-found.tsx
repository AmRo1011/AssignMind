/**
 * AssignMind — 404 Not Found Page
 */

import Link from "next/link";

export default function NotFound() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-background text-center px-4">
            <h1 className="text-8xl font-bold font-[family-name:var(--font-outfit)] text-primary/30">
                404
            </h1>
            <h2 className="mt-4 text-2xl font-semibold text-foreground">
                Page Not Found
            </h2>
            <p className="mt-2 max-w-md text-muted-foreground">
                The page you&apos;re looking for doesn&apos;t exist or has been moved.
            </p>
            <Link
                href="/"
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5"
            >
                Back to Dashboard
            </Link>
        </div>
    );
}
