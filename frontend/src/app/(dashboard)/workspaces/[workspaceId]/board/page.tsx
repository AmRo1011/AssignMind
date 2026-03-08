"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPatch } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useToast } from "@/providers/ToastProvider";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { KanbanCard } from "./KanbanCard";
import type { WorkspaceResponse } from "@/types/workspaces";
import type { TaskResponse } from "@/types/tasks";

type ColumnStatus = "todo" | "in_progress" | "done";

const COLUMNS: { id: ColumnStatus; label: string }[] = [
    { id: "todo", label: "To Do" },
    { id: "in_progress", label: "In Progress" },
    { id: "done", label: "Done" }
];

export default function KanbanBoardPage({ params }: { params: Promise<{ workspaceId: string }> }) {
    const { workspaceId } = use(params);
    const { user } = useCurrentUser();
    const router = useRouter();
    const { addToast } = useToast();

    const [ws, setWs] = useState<WorkspaceResponse | null>(null);
    const [tasks, setTasks] = useState<TaskResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [draggingId, setDraggingId] = useState<string | null>(null);

    const loadBoard = async () => {
        setLoading(true);
        try {
            const [wData, tData] = await Promise.all([
                apiGet<WorkspaceResponse>(`/workspaces/${workspaceId}`),
                apiGet<TaskResponse[]>(`/workspaces/${workspaceId}/tasks`)
            ]);
            setWs(wData);
            setTasks(tData);
        } catch (err: any) {
            addToast("error", "Failed to load Kanban board metadata.");
            if (err.status === 403 || err.status === 404) router.push("/dashboard");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadBoard(); }, [workspaceId]);

    const handleDragStart = (id: string, e: React.DragEvent) => {
        setDraggingId(id);
        e.dataTransfer.setData("taskId", id);
    };

    const handleDrop = async (e: React.DragEvent, status: ColumnStatus) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData("taskId");
        setDraggingId(null);

        if (!taskId) return;

        const taskIndex = tasks.findIndex(t => t.id === taskId);
        if (taskIndex === -1) return;
        const task = tasks[taskIndex];
        if (!task) return;

        if (task.status === status) return; // No change

        // Optimistic UI update
        const previousStatus = task.status;
        setTasks(prev => {
            const next = [...prev];
            next[taskIndex] = { ...task, status } as TaskResponse;
            return next;
        });

        try {
            await apiPatch(`/workspaces/${workspaceId}/tasks/${taskId}`, { status });
        } catch (err: any) {
            addToast("error", err.message || "Failed to update task status.");
            // Revert optimistically mapped UI
            setTasks(prev => {
                const revert = [...prev];
                revert[taskIndex] = { ...task, status: previousStatus } as TaskResponse;
                return revert;
            });
        }
    };

    if (loading || !ws) {
        return <div className="p-12 center flex justify-center"><Spinner size="lg" /></div>;
    }

    const canDrag = (t: TaskResponse) => {
        if (ws.role === "leader") return true;
        return t.assigned_to === user?.id;
    };

    return (
        <div className="p-8 max-w-[1400px] mx-auto space-y-8 min-h-screen flex flex-col">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">Board: {ws.title}</h1>
                    <p className="text-muted text-lg mt-1">Manage state triggers dragging and dropping logic.</p>
                </div>
                <Button variant="secondary" onClick={loadBoard}>Refresh Board</Button>
            </div>

            <div className="flex gap-6 flex-1 items-stretch py-4 overflow-x-auto min-h-[600px]">
                {COLUMNS.map(col => {
                    const columnTasks = tasks.filter(t => t.status === col.id).sort((a, b) => a.position - b.position);

                    return (
                        <div
                            key={col.id}
                            className="bg-muted/10 border border-border rounded-2xl flex-1 min-w-[320px] max-w-lg flex flex-col pt-4"
                            onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }}
                            onDrop={(e) => handleDrop(e, col.id)}
                        >
                            <div className="px-6 flex justify-between items-center mb-4 border-b border-border/50 pb-4">
                                <h3 className="font-bold text-foreground text-lg">{col.label}</h3>
                                <span className="text-xs bg-muted/20 px-2 py-1 rounded-full font-semibold text-muted">
                                    {columnTasks.length}
                                </span>
                            </div>

                            <div className="flex-1 p-4 pt-0 overflow-y-auto space-y-3 pb-8 h-full">
                                {columnTasks.map(t => (
                                    <div
                                        draggable={canDrag(t)}
                                        onDragStart={(e) => handleDragStart(t.id, e)}
                                        key={t.id}
                                        className={draggingId === t.id ? "opacity-50" : ""}
                                    >
                                        <KanbanCard
                                            task={t}
                                            members={ws.members || []}
                                            isDraggable={canDrag(t)}
                                            onDragStart={() => { }}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
