"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { apiGet } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { CreateWorkspaceModal } from "./CreateWorkspaceModal";
import { PendingInvitations } from "./PendingInvitations";
import type { WorkspaceResponse } from "@/types/workspaces";

export default function DashboardPage() {
    const { user, isLoading: userLoading } = useCurrentUser();
    const { addToast } = useToast();
    const [workspaces, setWorkspaces] = useState<WorkspaceResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    useEffect(() => { if (!userLoading && user) fetchWorkspaces(); }, [user, userLoading]);

    const fetchWorkspaces = async () => {
        try {
            setLoading(true);
            setWorkspaces(await apiGet<WorkspaceResponse[]>("/workspaces"));
        } catch {
            addToast("error", "Failed to load workspaces.");
        } finally { setLoading(false); }
    };

    if (userLoading || loading) return <div className="p-12 center"><Spinner size="lg" /></div>;

    return (
        <div className="flex flex-col gap-6">
            <div className="flex justify-between items-center mb-4">
                <div>
                    <h2 className="text-2xl font-bold font-[family-name:var(--font-outfit)]">
                        Welcome, {user?.full_name?.split(" ")[0]}!
                    </h2>
                    <p className="text-muted">Manage your workspaces and assignments.</p>
                </div>
                <Button onClick={() => setIsCreateOpen(true)}>+ Create Workspace</Button>
            </div>

            <PendingInvitations onHandled={fetchWorkspaces} />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workspaces.length === 0 ? (
                    <div className="col-span-full py-12 rounded-2xl border-2 border-dashed flex flex-col items-center">
                        <p className="text-muted font-medium mb-4">No active workspaces</p>
                        <Button variant="secondary" onClick={() => setIsCreateOpen(true)}>Create One</Button>
                    </div>
                ) : workspaces.map(w => (
                    <Link key={w.id} href={`/workspaces/${w.id}`} className="group relative block p-6 border rounded-2xl hover:border-primary/50 bg-surface shadow-sm transition duration-200">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="font-bold text-lg group-hover:text-primary transition">{w.title}</h3>
                            <span className="text-xs bg-muted/20 px-2 py-1 rounded-full uppercase text-muted font-semibold">{w.role || "Member"}</span>
                        </div>
                        <p className="text-sm text-muted line-clamp-2">{w.description || "No description provided."}</p>
                    </Link>
                ))}
            </div>

            <CreateWorkspaceModal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} onCreated={fetchWorkspaces} />
        </div>
    );
}
