"use client";

/**
 * AssignMind — Sidebar Component
 *
 * Left navigation sidebar displaying primary links, workspace list,
 * and the credit badge.
 */

import Link from "next/link";
import { CreditBadge } from "@/components/layout/CreditBadge";
import { APP_NAME } from "@/lib/constants";
import { SidebarNav } from "./SidebarNav";
import { SidebarWorkspaces } from "./SidebarWorkspaces";

export function Sidebar() {
    return (
        <aside className="w-64 flex-shrink-0 bg-surface border-r border-border flex flex-col h-screen sticky top-0">
            <div className="p-6 border-b border-border">
                <Link href="/" className="flex items-center gap-3 w-fit outline-none">
                    <div className="h-8 w-8 rounded-lg bg-primary text-white flex items-center justify-center font-bold text-lg font-[family-name:var(--font-outfit)] shadow-lg shadow-primary/25">
                        A
                    </div>
                    <span className="text-xl font-bold font-[family-name:var(--font-outfit)] tracking-tight text-foreground">
                        {APP_NAME}
                    </span>
                </Link>
            </div>

            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-6">
                <SidebarNav />
                <SidebarWorkspaces />
            </div>

            <div className="p-4 border-t border-border bg-surface">
                <CreditBadge />
            </div>
        </aside>
    );
}
