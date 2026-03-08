"use client";

/**
 * AssignMind — Workspace Sub-Navigation
 *
 * Horizontal navigation tabs for workspace pages.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

interface WorkspaceNavProps {
    workspaceId: string;
}

export function WorkspaceNav({ workspaceId }: WorkspaceNavProps) {
    const pathname = usePathname();
    const base = `/workspaces/${workspaceId}`;

    const links = [
        { href: base, label: "Overview", exact: true },
        { href: `${base}/assignment`, label: "Assignment", exact: false },
        { href: `${base}/distribute`, label: "Distribute", exact: false },
        { href: `${base}/board`, label: "Kanban Board", exact: false },
        { href: `${base}/chat`, label: "Chat", exact: false },
    ];

    return (
        <nav className="flex gap-1 border-b border-border mb-6 overflow-x-auto">
            {links.map((link) => {
                const active = link.exact
                    ? pathname === link.href
                    : pathname.startsWith(link.href);

                return (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${active
                                ? "border-primary text-primary"
                                : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted"
                            }`}
                    >
                        {link.label}
                    </Link>
                );
            })}
        </nav>
    );
}
