"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api";
import { useAuth } from "@/providers/AuthProvider";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function ReactivatePage() {
    const [isLoading, setIsLoading] = useState(false);
    const { signOut } = useAuth();
    const { addToast } = useToast();
    const router = useRouter();

    const handleReactivate = async () => {
        try {
            setIsLoading(true);
            await apiPost("/users/me/reactivate", {});
            addToast("success", "Account restored successfully!");
            router.push("/callback"); // Retrigger the callback logic
        } catch (err) {
            addToast("error", err instanceof Error ? err.message : "Failed to restore account");
            setIsLoading(false);
        }
    };

    const handleCancel = async () => {
        await signOut();
        router.push("/login");
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-surface p-4">
            <Card className="w-full max-w-md p-8 text-center">
                <div className="mb-6 flex justify-center">
                    <svg className="w-16 h-16 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                </div>
                <h2 className="text-2xl font-bold font-[family-name:var(--font-outfit)] text-foreground mb-4">
                    Account Deactivated
                </h2>
                <p className="text-muted text-sm mb-8">
                    Your account is currently within its 14-day grace period. Would you like to restore it and continue using AssignMind?
                </p>

                <div className="flex flex-col gap-3">
                    <Button onClick={handleReactivate} isLoading={isLoading} className="w-full">
                        Restore My Account
                    </Button>
                    <Button onClick={handleCancel} disabled={isLoading} variant="ghost" className="w-full">
                        Cancel and Log Out
                    </Button>
                </div>
            </Card>
        </div>
    );
}
