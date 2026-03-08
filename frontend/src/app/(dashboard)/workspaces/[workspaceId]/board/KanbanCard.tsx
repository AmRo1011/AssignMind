"use client";

import { useMemo } from "react";
import { Avatar } from "@/components/ui/Avatar";
import type { TaskResponse } from "@/types/tasks";
import type { WorkspaceMemberResponse } from "@/types/workspaces";

interface KanbanCardProps {
    task: TaskResponse;
    members: WorkspaceMemberResponse[];
    isDraggable: boolean;
    onDragStart: (taskId: string) => void;
}

export function KanbanCard({ task, members, isDraggable, onDragStart }: KanbanCardProps) {
    const assignee = useMemo(() => {
        if (!task.assigned_to) return null;
        return members.find(m => m.user_id === task.assigned_to)?.user || null;
    }, [task.assigned_to, members]);

    const isOverdue = useMemo(() => {
        if (!task.deadline || task.status === "done") return false;
        return new Date(task.deadline) < new Date();
    }, [task.deadline, task.status]);

    return (
        <div
            draggable={isDraggable}
            onDragStart={(e) => {
                e.dataTransfer.setData("text/plain", task.id);
                onDragStart(task.id);
            }}
            className={`p-4 rounded-xl border bg-surface shadow-sm transition-shadow hover:shadow-md cursor-grab active:cursor-grabbing ${isOverdue ? "border-error/50 bg-error/5" : "border-border"
                }`}
        >
            <div className="flex justify-between items-start mb-2 gap-2">
                <h4 className="font-semibold text-sm leading-tight text-foreground line-clamp-2" title={task.title}>
                    {task.title}
                </h4>
                {task.is_ai_generated && <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded uppercase font-bold tracking-wide flex-shrink-0">AI</span>}
            </div>

            <p className="text-xs text-muted mb-4 line-clamp-2">{task.description}</p>

            <div className="flex items-center justify-between mt-auto pt-2 border-t border-border/50">
                <div className="flex items-center gap-2">
                    {assignee ? (
                        <Avatar src={assignee.avatar_url} name={assignee.full_name} size="sm" />
                    ) : (
                        <div className="h-8 w-8 rounded-full bg-muted/20 flex items-center justify-center border border-dashed border-muted text-muted text-xs">
                            ?
                        </div>
                    )}
                    <span className="text-xs font-medium text-foreground truncate max-w-[100px]">
                        {assignee ? assignee.full_name.split(" ")[0] : "Unassigned"}
                    </span>
                </div>

                {task.deadline && (
                    <div className={`text-xs font-medium ${isOverdue ? "text-error" : "text-muted"}`}>
                        {new Date(task.deadline).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                    </div>
                )}
            </div>
        </div>
    );
}
