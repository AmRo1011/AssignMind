/**
 * AssignMind — Datetime Utilities
 *
 * UTC timestamps from the backend are formatted for display
 * using the browser's Intl.DateTimeFormat. No timezone libraries
 * needed — the browser handles conversion natively.
 */

/** Format a UTC ISO string to localized date+time. */
export function formatDateTime(isoString: string, locale?: string): string {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat(locale ?? navigator.language, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
    }).format(date);
}

/** Format a UTC ISO string to localized date only. */
export function formatDate(isoString: string, locale?: string): string {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat(locale ?? navigator.language, {
        year: "numeric",
        month: "short",
        day: "numeric",
    }).format(date);
}

/** Format a UTC ISO string to localized time only. */
export function formatTime(isoString: string, locale?: string): string {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat(locale ?? navigator.language, {
        hour: "numeric",
        minute: "2-digit",
    }).format(date);
}

/** Get relative time (e.g., "5 minutes ago", "in 2 hours"). */
export function formatRelativeTime(isoString: string): string {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);

    const rtf = new Intl.RelativeTimeFormat(navigator.language, {
        numeric: "auto",
    });

    if (Math.abs(diffSeconds) < 60) return rtf.format(-diffSeconds, "second");
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (Math.abs(diffMinutes) < 60) return rtf.format(-diffMinutes, "minute");
    const diffHours = Math.floor(diffMinutes / 60);
    if (Math.abs(diffHours) < 24) return rtf.format(-diffHours, "hour");
    const diffDays = Math.floor(diffHours / 24);
    return rtf.format(-diffDays, "day");
}

/** Check if a deadline is overdue. */
export function isOverdue(isoString: string): boolean {
    return new Date(isoString) < new Date();
}

/** Get hours remaining until a deadline. */
export function hoursUntil(isoString: string): number {
    const target = new Date(isoString);
    const now = new Date();
    return (target.getTime() - now.getTime()) / (1000 * 60 * 60);
}
