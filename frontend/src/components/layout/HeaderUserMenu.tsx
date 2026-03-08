"use client";

import { useState } from "react";
import { useAuth } from "@/providers/AuthProvider";
import { Avatar } from "@/components/ui/Avatar";
import type { User } from "@/types/user";

export function HeaderUserMenu({ user }: { user: User }) {
    const { signOut } = useAuth();
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <div className="flex items-center gap-3 relative">
            <span className="text-sm font-medium text-foreground">{user.full_name}</span>
            <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 ring-offset-surface transition-shadow"
                aria-label="User menu" aria-expanded={menuOpen} aria-haspopup="true"
            >
                <Avatar name={user.full_name} src={user.avatar_url} size="md" />
            </button>

            {menuOpen && (
                <div className="absolute top-14 right-0 mt-2 w-48 rounded-xl bg-surface border border-border shadow-xl py-1 animate-[scaleIn_0.15s_ease-out] origin-top-right z-50">
                    <div className="px-4 py-3 border-b border-border">
                        <p className="text-sm font-semibold text-foreground truncate">{user.full_name}</p>
                        <p className="text-xs text-muted truncate">{user.email}</p>
                    </div>
                    <button
                        onClick={signOut}
                        className="w-full text-left px-4 py-2 text-sm text-error hover:bg-error/10 transition-colors"
                    >
                        Sign Out
                    </button>
                </div>
            )}
        </div>
    );
}
