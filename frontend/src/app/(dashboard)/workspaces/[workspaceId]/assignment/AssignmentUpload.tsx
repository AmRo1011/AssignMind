"use client";

import { useState } from "react";
import { useToast } from "@/providers/ToastProvider";
import { apiUpload } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { AssignmentResponse } from "@/types/assignments";

export default function AssignmentUpload({ workspaceId, onUploadSuccess }: { workspaceId: string; onUploadSuccess: (a: AssignmentResponse) => void }) {
    const { addToast } = useToast();
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);

    const handleUpload = async () => {
        if (!file || !window.confirm("This action costs 10 credits. Proceed?")) return;
        setIsUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await apiUpload<AssignmentResponse>(`/workspaces/${workspaceId}/assignments`, formData);
            addToast("success", "Assignment processed!");
            onUploadSuccess(res);
        } catch (err: any) {
            addToast("error", err.message || "Upload failed.");
            setIsUploading(false);
        }
    };

    return (
        <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">Upload Assignment</h2>
            <p className="text-sm text-muted mb-4 opacity-75">Costs 10 credits (PDF/TXT, 10MB Max)</p>
            <input
                type="file" accept=".pdf,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mb-4 block w-full text-sm text-foreground file:mr-4 file:py-1 file:px-2 file:rounded-md file:border-0 file:bg-primary file:text-primary-foreground"
            />
            <Button onClick={handleUpload} disabled={!file || isUploading} isLoading={isUploading}>
                Extract & Analyze Document
            </Button>
        </Card>
    );
}
