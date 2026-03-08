"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { useToast } from "@/providers/ToastProvider";
import { apiPost } from "@/lib/api";
import type { WorkspaceResponse } from "@/types/workspaces";

interface SettingsProps {
    isOpen: boolean; onClose: () => void; ws: WorkspaceResponse;
}

export function WorkspaceSettingsModal({ isOpen, onClose, ws }: SettingsProps) {
    const { addToast } = useToast();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [selectedLeader, setSelectedLeader] = useState<string>("");

    if (ws.role !== "leader") return null;

    const handleTransfer = async () => {
        if (!selectedLeader || !window.confirm("Are you sure? You cannot undo this unless the new leader transfers it back.")) return;
        setLoading(true);
        try {
            await apiPost(`/workspaces/${ws.id}/transfer-leadership`, { new_leader_id: selectedLeader });
            addToast("success", "Leadership transferred successfully.");
            onClose(); router.refresh();
        } catch (err: any) { addToast("error", err.message || "Failed to transfer"); }
        finally { setLoading(false); }
    };

    const handleArchive = async () => {
        if (!window.confirm("Are you sure you want to archive this workspace?")) return;
        setLoading(true);
        try {
            await apiPost(`/workspaces/${ws.id}/archive`);
            addToast("success", "Workspace archived.");
            router.push("/dashboard");
        } catch (err: any) { addToast("error", err.message || "Failed to archive"); }
        finally { setLoading(false); }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Workspace Settings">
            <div className="space-y-6">
                <div className="border border-border p-4 rounded-xl">
                    <h3 className="font-semibold mb-2">Transfer Leadership</h3>
                    <p className="text-sm text-muted mb-4">Pass the Team Leader role to another member.</p>
                    <div className="flex gap-2">
                        <select className="flex-1 bg-surface border rounded text-sm p-2"
                            value={selectedLeader} onChange={e => setSelectedLeader(e.target.value)}>
                            <option value="">Select new leader...</option>
                            {ws.members?.filter(m => m.user_id !== ws.created_by).map(m => (
                                <option key={m.user_id} value={m.user_id}>{m.user?.full_name || m.user?.email}</option>
                            ))}
                        </select>
                        <Button size="sm" onClick={handleTransfer} disabled={!selectedLeader || loading}>Transfer</Button>
                    </div>
                </div>

                <div className="border border-destructive/20 bg-destructive/5 p-4 rounded-xl">
                    <h3 className="font-semibold text-destructive mb-2">Danger Zone</h3>
                    <p className="text-sm text-muted mb-4">Archiving drops this space from open views.</p>
                    <Button variant="secondary" className="border-destructive text-destructive" onClick={handleArchive} isLoading={loading}>
                        Archive Workspace
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
