"use client";

/**
 * AssignMind — Header Component
 *
 * Top navigation bar showing the page title and user avatar profile menu.
 */

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { Spinner } from "@/components/ui/Spinner";
import { HeaderUserMenu } from "./HeaderUserMenu";

interface HeaderProps {
    title?: string;
}

export function Header({ title }: HeaderProps) {
    const { user, isLoading } = useCurrentUser();

    return (
        <header className="h-20 bg-surface/80 backdrop-blur-md border-b border-border flex items-center justify-between px-8 sticky top-0 z-40">
            <h1 className="text-2xl font-bold text-foreground font-[family-name:var(--font-outfit)]">
                {title || "Dashboard"}
            </h1>

            <div className="flex items-center gap-4 relative">
                {isLoading && <Spinner size="sm" />}
                {!isLoading && user && <HeaderUserMenu user={user} />}
            </div>
        </header>
    );
}
