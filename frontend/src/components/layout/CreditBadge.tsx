"use client";

/**
 * AssignMind — Credit Badge Component
 *
 * Displays the user's available credit balance. Shows a warning badge
 * when the balance dips to or below the low credit threshold.
 */

import Link from "next/link";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { Badge } from "@/components/ui/Badge";
import { LOW_CREDIT_THRESHOLD } from "@/lib/constants";
import { Spinner } from "@/components/ui/Spinner";

export function CreditBadge() {
    const { user, isLoading } = useCurrentUser();

    if (isLoading) {
        return (
            <div className="flex items-center gap-2 p-3 text-sm rounded-lg bg-surface border border-border">
                <Spinner size="sm" className="opacity-50" />
                <span className="text-muted">Loading credits...</span>
            </div>
        );
    }

    if (!user) return null;

    const isLow = user.credit_available <= LOW_CREDIT_THRESHOLD;

    return (
        <Link href="/credits" className="block outline-none group rounded-xl">
            <div className="flex items-center justify-between p-3 rounded-lg bg-surface border border-border group-hover:border-primary/30 transition-colors cursor-pointer">
                <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zM8.5 7a1.5 1.5 0 113 0v1h-3v-1zm1.5 4a1.5 1.5 0 00-1.5 1.5v2A1.5 1.5 0 0010 16a1.5 1.5 0 001.5-1.5v-2A1.5 1.5 0 0010 11z" clipRule="evenodd" />
                    </svg>
                    <div className="flex flex-col">
                        <span className="text-xs font-semibold text-muted uppercase tracking-wider">
                            Credits
                        </span>
                        <span className="text-sm font-bold text-foreground font-[family-name:var(--font-outfit)]">
                            {user.credit_available}
                        </span>
                    </div>
                </div>
                {isLow && (
                    <Badge variant="warning" className="ml-2">Low</Badge>
                )}
            </div>
        </Link>
    );
}
