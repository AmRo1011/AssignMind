"use client";

import { useEffect, useState, use } from "react";
import { apiGet } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Spinner } from "@/components/ui/Spinner";
import type { AssignmentResponse } from "@/types/assignments";
import AssignmentUpload from "./AssignmentUpload";
import AssignmentSummaryCard from "./AssignmentSummaryCard";
import { Button } from "@/components/ui/Button";

interface PageProps {
    workspaceId: string;
}

export default function AssignmentPage({ workspaceId }: PageProps) {
    const { addToast } = useToast();
    const [assignment, setAssignment] = useState<AssignmentResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchLatest();
    }, [workspaceId]);

    const fetchLatest = async () => {
        try {
            const data = await apiGet<AssignmentResponse>(`/workspaces/${workspaceId}/assignments/latest`);
            setAssignment(data);
        } catch (err: any) {
            if (err.status !== 404) addToast("error", "Error loading assignment");
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div className="p-8 flex justify-center"><Spinner size="lg" /></div>;
    }

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">Assignment Hub</h1>
                    <p className="text-muted">Analyze course payloads and define goals.</p>
                </div>
            </div>

            {assignment ? (
                <div className="space-y-6">
                    <AssignmentSummaryCard summary={assignment.structured_summary} version={assignment.version} />
                    <AssignmentUpload workspaceId={workspaceId} onUploadSuccess={(data) => setAssignment(data)} />
                </div>
            ) : (
                <AssignmentUpload workspaceId={workspaceId} onUploadSuccess={(data) => setAssignment(data)} />
            )}
        </div>
    );
}
