"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { InviteMemberModal } from "./InviteMemberModal";
import { WorkspaceSettingsModal } from "./WorkspaceSettingsModal";
import { WorkspaceNav } from "@/components/layout/WorkspaceNav";
import type { WorkspaceResponse } from "@/types/workspaces";

export default function WorkspacePage({ params }: { params: Promise<{ workspaceId: string }> }) {
    const { workspaceId } = use(params);
    const [ws, setWs] = useState<WorkspaceResponse | null>(null);
    const [inviteOpen, setInviteOpen] = useState(false);
    const [settingsOpen, setSettingsOpen] = useState(false);

    useEffect(() => {
        apiGet<WorkspaceResponse>(`/workspaces/${workspaceId}`).then(setWs).catch(() => { });
    }, [workspaceId]);

    if (!ws) return <div className="p-12 center flex justify-center"><Spinner size="lg" /></div>;

    const leaderName = ws.members?.find(m => m.user_id === ws.created_by)?.user?.full_name || "Unknown";

    return (
        <div className="max-w-5xl mx-auto space-y-8 p-6">
            <div className="flex justify-between items-start">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">{ws.title}</h1>
                        <span className="text-xs bg-muted/20 px-2 py-1 rounded-full uppercase text-muted font-bold">{ws.role}</span>
                    </div>
                    <p className="text-muted text-lg">{ws.description}</p>
                </div>
                {ws.role === "leader" && (
                    <Button variant="secondary" onClick={() => setSettingsOpen(true)}>Settings</Button>
                )}
            </div>

            <WorkspaceNav workspaceId={workspaceId} />

            <div>
                <div className="flex items-center justify-between border-b pb-4 mb-6">
                    <h2 className="text-xl font-bold">Team Members ({ws.members?.length || 0}/10)</h2>
                    {ws.role === "leader" && <Button size="sm" onClick={() => setInviteOpen(true)}>+ Invite Members</Button>}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {ws.members?.map(m => (
                        <div key={m.id} className="flex items-center gap-4 bg-muted/10 p-4 border rounded-xl">
                            <Avatar src={m.user?.avatar_url || null} name={m.user?.full_name || "?"} size="md" />
                            <div>
                                <p className="font-semibold text-sm">{m.user?.full_name}</p>
                                <p className="text-xs text-muted capitalize">{m.role}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <WorkspaceSettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} ws={ws} />
            <InviteMemberModal isOpen={inviteOpen} onClose={() => setInviteOpen(false)} workspaceId={workspaceId} />
        </div>
    );
}
