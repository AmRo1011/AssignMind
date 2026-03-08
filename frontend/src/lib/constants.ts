/**
 * AssignMind — Application Constants
 *
 * App-wide configuration values. Read from environment where
 * available, with sensible defaults.
 */

/** Chat polling interval in milliseconds (30 seconds). */
export const CHAT_POLL_INTERVAL_MS =
    Number(process.env.NEXT_PUBLIC_CHAT_POLL_INTERVAL_MS) || 30_000;

/** Show low-balance warning when credits ≤ this threshold. */
export const LOW_CREDIT_THRESHOLD =
    Number(process.env.NEXT_PUBLIC_LOW_CREDIT_THRESHOLD) || 10;

/** Maximum workspace members (including leader). */
export const MAX_WORKSPACE_MEMBERS = 10;

/** Maximum file upload size in bytes (10 MB). */
export const MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024;

/** Accepted file MIME types for assignment upload. */
export const ACCEPTED_FILE_TYPES = [
    "application/pdf",
    "text/plain",
] as const;

/** Accepted file extensions for display. */
export const ACCEPTED_FILE_EXTENSIONS = ".pdf, .txt";

/** Credit costs for AI operations. */
export const CREDIT_COSTS = {
    ASSIGNMENT_ANALYSIS: 10,
    TASK_DISTRIBUTION: 5,
} as const;

/** Initial free credits granted on registration. */
export const FREE_CREDITS = 30;

/** Credit package options for purchase. */
export const CREDIT_PACKAGES = [
    { name: "Starter", credits: 100, priceUsd: 2 },
    { name: "Standard", credits: 300, priceUsd: 5 },
    { name: "Pro", credits: 700, priceUsd: 10 },
] as const;

/** Task status values. */
export const TASK_STATUSES = ["todo", "in_progress", "done"] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];

/** Workspace member roles. */
export const MEMBER_ROLES = ["leader", "member"] as const;
export type MemberRole = (typeof MEMBER_ROLES)[number];

/** Application name. */
export const APP_NAME =
    process.env.NEXT_PUBLIC_APP_NAME ?? "AssignMind";
