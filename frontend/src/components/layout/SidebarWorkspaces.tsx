"use client";

import Link from "next/link";

export function SidebarWorkspaces() {
    return (
        <div className="flex flex-col gap-2 flex-1">
            <div className="flex items-center justify-between px-3 text-xs font-semibold uppercase tracking-wider text-muted">
                <span>Your Workspaces</span>
                <Link href="/workspaces/new" className="hover:text-primary transition-colors focus-visible:outline-none" aria-label="Create workspace">
                    +
                </Link>
            </div>
            <div className="px-3 text-sm text-muted">
                {/* The workspaces array mapping will go here in Phase 4 */}
                <span className="italic">No workspaces yet</span>
            </div>
        </div>
    );
}
