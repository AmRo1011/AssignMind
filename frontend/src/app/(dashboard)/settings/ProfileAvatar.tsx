"use client";

import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import type { UserWithCredits } from "@/types/user";

export function ProfileAvatar({ user }: { user: UserWithCredits }) {
    return (
        <>
            <div className="flex items-center gap-4 mb-6">
                <Avatar name={user.full_name} src={user.avatar_url} size="lg" />
                <div className="flex flex-col">
                    <span className="text-lg font-semibold text-foreground">{user.full_name}</span>
                    <span className="text-sm text-muted">{user.email}</span>
                </div>
            </div>
            <Input label="Phone Number" value={user.phone || ""} disabled helperText="Verified securely via SMS" />
        </>
    );
}

// Temporary import placeholder
import { Input } from "@/components/ui/Input";
