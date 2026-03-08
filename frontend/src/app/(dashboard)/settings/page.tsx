"use client";

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { ProfileForm } from "./ProfileForm";
import { DangerZone } from "./DangerZone";
import { Spinner } from "@/components/ui/Spinner";

export default function SettingsPage() {
    const { user, isLoading } = useCurrentUser();

    if (isLoading || !user) {
        return (
            <div className="flex h-full items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-8 max-w-2xl mx-auto pb-12 w-full">
            <div>
                <h2 className="text-2xl font-bold text-foreground font-[family-name:var(--font-outfit)]">
                    Account Settings
                </h2>
                <p className="text-muted mt-1">
                    Manage your profile, preferences, and account security.
                </p>
            </div>

            <div className="grid gap-6">
                <ProfileForm user={user} />
                <DangerZone />
            </div>
        </div>
    );
}
