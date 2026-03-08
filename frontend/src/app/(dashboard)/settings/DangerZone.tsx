"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api";
import { useAuth } from "@/providers/AuthProvider";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DangerZoneModal } from "./DangerZoneModal";

export function DangerZone() {
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { signOut } = useAuth();
    const { addToast } = useToast();
    const router = useRouter();

    const handleDelete = async () => {
        try {
            setIsLoading(true);
            await apiPost("/users/me/delete", {});
            addToast("success", "Account deactivated. You have 14 days to restore it.");
            await signOut();
            router.push("/login");
        } catch (err) {
            addToast("error", err instanceof Error ? err.message : "Failed to delete account");
            setIsLoading(false);
        }
    };

    return (
        <Card className="border-error/20 bg-error/5">
            <CardHeader title="Danger Zone" action={<Badge variant="error" className="uppercase text-[10px]">Irreversible</Badge>} />
            <div className="flex flex-col gap-4">
                <div>
                    <h4 className="font-semibold text-foreground text-sm">Delete Account</h4>
                    <p className="text-sm text-muted mt-1">
                        Once you delete your account, there is no going back after the 14-day grace period.
                    </p>
                </div>
                <Button variant="danger" className="w-fit" onClick={() => setIsOpen(true)}>
                    Delete Account
                </Button>
            </div>

            <DangerZoneModal
                isOpen={isOpen} isLoading={isLoading}
                onClose={() => setIsOpen(false)} onConfirm={handleDelete}
            />
        </Card>
    );
}
