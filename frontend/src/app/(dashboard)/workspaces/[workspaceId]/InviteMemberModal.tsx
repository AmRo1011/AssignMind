"use client";

import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/providers/ToastProvider";
import { apiPost, apiGet } from "@/lib/api";
import type { InvitationResponse } from "@/types/workspaces";

export function InviteMemberModal({ isOpen, onClose, workspaceId }: { isOpen: boolean, onClose: () => void, workspaceId: string }) {
    const { addToast } = useToast();
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [invites, setInvites] = useState<InvitationResponse[]>([]);

    useEffect(() => { if (isOpen) fetchInvites(); }, [isOpen]);

    const fetchInvites = async () => {
        try { setInvites(await apiGet(`/workspaces/${workspaceId}/invitations`)); }
        catch { /* ignored */ }
    };

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await apiPost(`/workspaces/${workspaceId}/invitations`, { email });
            addToast("success", `Invite sent to ${email}`);
            setEmail("");
            fetchInvites();
        } catch (err: any) {
            addToast("error", err.message || "Failed to invite");
        } finally { setLoading(false); }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Manage Team & Invites">
            <div className="space-y-6">
                <form onSubmit={handleInvite} className="flex gap-2 items-end">
                    <div className="flex-1"><Input label="Email address" type="email" value={email} onChange={e => setEmail(e.target.value)} required /></div>
                    <Button type="submit" isLoading={loading} className="mb-0">Send Invite</Button>
                </form>

                <div className="border-t pt-4">
                    <h4 className="text-sm font-semibold mb-3">Pending Invitations ({invites.length})</h4>
                    {invites.length === 0 ? <p className="text-sm text-muted">No pending invites.</p> : (
                        <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                            {invites.map(i => (
                                <div key={i.id} className="flex justify-between items-center bg-muted/10 p-2 rounded text-sm">
                                    <span>{i.email}</span>
                                    <span className="text-xs text-muted/60 capitalize">{i.status}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </Modal>
    );
}
