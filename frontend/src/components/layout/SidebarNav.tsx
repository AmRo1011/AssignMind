"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function SidebarNav() {
    const pathname = usePathname();
    const links = [
        { href: "/", label: "Dashboard", match: "/" },
        { href: "/workspaces", label: "Workspaces", match: "/workspaces" },
        { href: "/settings", label: "Settings", match: "/settings" },
        { href: "/credits", label: "Credits & Billing", match: "/credits" },
    ];

    return (
        <nav className="flex flex-col gap-1">
            {links.map((link) => {
                const active = link.match === "/"
                    ? pathname === "/" : pathname.startsWith(link.match);
                return (
                    <Link
                        key={link.href} href={link.href}
                        className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-primary ${active ? "bg-primary/10 text-primary" : "text-muted hover:bg-surface-hover hover:text-foreground"
                            }`}
                    >
                        {link.label}
                    </Link>
                );
            })}
        </nav>
    );
}
