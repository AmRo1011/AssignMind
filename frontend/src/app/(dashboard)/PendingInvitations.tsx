"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { InvitationWithWorkspaceResponse } from "@/types/workspaces";

export function PendingInvitations({ onHandled }: { onHandled: () => void }) {
    const { addToast } = useToast();
    const [invites, setInvites] = useState<InvitationWithWorkspaceResponse[]>([]);

    useEffect(() => { loadInvites(); }, []);

    const loadInvites = async () => {
        try {
            setInvites(await apiGet<InvitationWithWorkspaceResponse[]>("/invitations/pending"));
        } catch {
            addToast("error", "Failed to load invitations");
        }
    };

    const handleAction = async (id: string, action: "accept" | "decline") => {
        try {
            await apiPost(`/invitations/${id}/${action}`);
            addToast("success", `Invitation ${action}ed`);
            setInvites(prev => prev.filter(i => i.id !== id));
            if (action === "accept") onHandled();
        } catch {
            addToast("error", `Failed to ${action}`);
        }
    };

    if (invites.length === 0) return null;

    return (
        <Card className="p-6 mb-8 bg-surface/50 border-primary/20">
            <h3 className="text-lg font-semibold mb-4 text-primary">Pending Invitations</h3>
            <div className="space-y-3">
                {invites.map(inv => (
                    <div key={inv.id} className="flex justify-between items-center bg-background p-3 rounded-lg border">
                        <div>
                            <p className="font-medium">{inv.workspace?.title || "Unknown Workspace"}</p>
                            <p className="text-xs text-muted">Sent to: {inv.email}</p>
                        </div>
                        <div className="flex gap-2">
                            <Button size="sm" onClick={() => handleAction(inv.id, "accept")}>Accept</Button>
                            <Button size="sm" variant="secondary" onClick={() => handleAction(inv.id, "decline")}>Decline</Button>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    );
}
