"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { WorkspaceResponse } from "@/types/workspaces";
import type { AssignmentResponse } from "@/types/assignments";
import type { TaskCreate, GeneratedTaskResponse } from "@/types/tasks";

export default function DistributePage({ params }: { params: Promise<{ workspaceId: string }> }) {
    const { workspaceId } = use(params);
    const router = useRouter();
    const { addToast } = useToast();

    const [ws, setWs] = useState<WorkspaceResponse | null>(null);
    const [assignment, setAssignment] = useState<AssignmentResponse | null>(null);
    const [loading, setLoading] = useState(true);

    const [step, setStep] = useState<"input" | "generating" | "review">("input");
    const [manualConstraints, setManualConstraints] = useState("");
    const [tasks, setTasks] = useState<TaskCreate[]>([]);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        Promise.all([
            apiGet<WorkspaceResponse>(`/workspaces/${workspaceId}`).catch(() => null),
            apiGet<AssignmentResponse>(`/workspaces/${workspaceId}/assignments/latest`).catch(() => null)
        ]).then(([w, a]) => {
            if (!w || w.role !== "leader") {
                addToast("error", "Access denied. Only Team Leaders can distribute tasks.");
                router.push(`/workspaces/${workspaceId}`);
                return;
            }
            if (!a) {
                addToast("error", "No assignment found. Please upload one first.");
                router.push(`/workspaces/${workspaceId}/assignment`);
                return;
            }
            setWs(w);
            setAssignment(a);
            setLoading(false);
        });
    }, [workspaceId, router]);

    const handleGenerate = async () => {
        if (!confirm("Generating an AI Distribution costs 5 credits. Continue?")) return;
        setStep("generating");
        try {
            const result = await apiPost<GeneratedTaskResponse[]>(`/workspaces/${workspaceId}/tasks/distribute`, {
                manual_constraints: manualConstraints || null
            });

            // Map strings to UUIDs
            const mapped = result.map(t => {
                let assigned_to: string | null = null;
                if (t.assigned_to) {
                    const match = ws?.members?.find(m =>
                        m.user?.full_name?.toLowerCase().includes(t.assigned_to!.toLowerCase()) ||
                        m.user?.email?.toLowerCase() === t.assigned_to!.toLowerCase()
                    );
                    if (match) assigned_to = match.user_id;
                }
                return {
                    title: t.title,
                    description: t.description,
                    assigned_to,
                    deadline: null,
                    status: "todo",
                    is_ai_generated: true
                };
            });
            setTasks(mapped);
            setStep("review");
        } catch (err: any) {
            addToast("error", err.message || "Failed to generate tasks.");
            setStep("input");
        }
    };

    const handleFinalize = async () => {
        setSaving(true);
        try {
            await apiPost(`/workspaces/${workspaceId}/tasks/finalize`, { tasks });
            addToast("success", "Tasks successfully mapped to board.");
            router.push(`/workspaces/${workspaceId}/board`);
        } catch (err: any) {
            addToast("error", err.message || "Finalization failed.");
            setSaving(false);
        }
    };

    const updateTask = (idx: number, field: keyof TaskCreate, value: any) => {
        setTasks(prev => {
            const copy = [...prev];
            (copy[idx] as any)[field] = value;
            return copy;
        });
    };

    if (loading) return <div className="p-12 center flex justify-center"><Spinner size="lg" /></div>;

    const autoConstraints = assignment?.structured_summary?.constraints || [];

    return (
        <div className="max-w-5xl mx-auto space-y-8 p-6">
            <div>
                <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">Task Distribution Engine</h1>
                <p className="text-muted text-lg mt-1">Split assignment requirements into team Kanban logic intelligently.</p>
            </div>

            {step === "input" && (
                <div className="space-y-6">
                    <div className="border p-6 rounded-2xl bg-surface/50 space-y-4">
                        <h2 className="text-xl font-bold">1. Review AI Triggers</h2>
                        <div className="bg-background border p-4 rounded-xl text-sm space-y-2">
                            <span className="font-semibold text-primary block">Extracted Rules:</span>
                            {autoConstraints.length === 0 ? <p className="text-muted">No explicit constraints extracted.</p> : (
                                <ul className="list-disc list-inside text-muted">
                                    {autoConstraints.map((c, i) => <li key={i}>{c}</li>)}
                                </ul>
                            )}
                        </div>
                        <div className="space-y-1">
                            <label className="text-sm font-semibold text-foreground">Manual Directives (Optional)</label>
                            <p className="text-xs text-muted mb-2">Inject prompt commands to guide the AI before distribution.</p>
                            <textarea
                                className="w-full flex min-h-[100px] rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                                placeholder="E.g., John must handle the Introduction paragraph. Prioritize backend mapping to Alice."
                                value={manualConstraints}
                                onChange={e => setManualConstraints(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="flex justify-end pt-2">
                        <Button onClick={handleGenerate} className="w-full sm:w-auto">✨ Generate Distribution (-5 Credits)</Button>
                    </div>
                </div>
            )}

            {step === "generating" && (
                <div className="p-12 flex flex-col items-center justify-center space-y-4 text-center bg-surface/50 border rounded-2xl py-24">
                    <Spinner size="lg" />
                    <h2 className="text-xl font-semibold">Orchestrating Deliverables...</h2>
                    <p className="text-muted max-w-sm">The Prompt Engine is analyzing requirements and dynamically mapping chunks into isolated Team Assignments.</p>
                </div>
            )}

            {step === "review" && (
                <div className="space-y-6">
                    <div className="border border-border rounded-xl overflow-hidden bg-surface">
                        <div className="border-b bg-muted/20 p-4 sticky top-0 font-semibold grid grid-cols-12 gap-4 text-sm">
                            <div className="col-span-3">Title</div>
                            <div className="col-span-5">Description</div>
                            <div className="col-span-2">Assignee</div>
                            <div className="col-span-2">Deadline</div>
                        </div>
                        <div className="divide-y max-h-[60vh] overflow-y-auto">
                            {tasks.map((t, i) => (
                                <div key={i} className="p-4 grid grid-cols-12 gap-4 items-start">
                                    <div className="col-span-3">
                                        <input type="text" className="w-full text-sm font-medium bg-transparent border-b border-transparent hover:border-border focus:border-primary outline-none focus:ring-0 px-1 py-0.5"
                                            value={t.title} onChange={e => updateTask(i, "title", e.target.value)} />
                                    </div>
                                    <div className="col-span-5">
                                        <textarea className="w-full text-xs text-muted bg-transparent border-b border-transparent hover:border-border focus:border-primary outline-none focus:ring-0 px-1 py-0.5 min-h-[60px] resize-y"
                                            value={t.description || ""} onChange={e => updateTask(i, "description", e.target.value)} />
                                    </div>
                                    <div className="col-span-2">
                                        <select className="w-full text-xs bg-surface border rounded-md px-2 py-1"
                                            value={t.assigned_to || ""} onChange={e => updateTask(i, "assigned_to", e.target.value || null)}>
                                            <option value="">Unassigned</option>
                                            {ws?.members?.map(m => (
                                                <option key={m.user_id} value={m.user_id}>{m.user?.full_name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="col-span-2">
                                        <input type="datetime-local" className="w-full text-xs bg-surface border rounded-md px-2 py-1"
                                            value={t.deadline ? new Date(t.deadline).toISOString().slice(0, 16) : ""}
                                            onChange={e => updateTask(i, "deadline", e.target.value ? new Date(e.target.value).toISOString() : null)} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="flex justify-between items-center">
                        <Button variant="secondary" onClick={() => setStep("input")} disabled={saving}>Discard Plan</Button>
                        <Button onClick={handleFinalize} isLoading={saving}>Finalize Task Layout</Button>
                    </div>
                </div>
            )}
        </div>
    );
}
