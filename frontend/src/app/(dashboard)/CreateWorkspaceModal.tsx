"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/providers/ToastProvider";
import { apiPost } from "@/lib/api";
import type { WorkspaceResponse } from "@/types/workspaces";

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (w: WorkspaceResponse) => void;
}

export function CreateWorkspaceModal({ isOpen, onClose, onCreated }: Props) {
    const { addToast } = useToast();
    const [title, setTitle] = useState("");
    const [desc, setDesc] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const w = await apiPost<WorkspaceResponse>("/workspaces", { title, description: desc });
            addToast("success", "Workspace created!");
            setTitle(""); setDesc("");
            onCreated(w);
            onClose();
        } catch (err: any) {
            addToast("error", err.message || "Creation failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create Workspace">
            <form onSubmit={handleSubmit} className="space-y-4">
                <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
                <div className="space-y-1">
                    <label className="text-sm font-medium text-foreground">Description</label>
                    <textarea
                        value={desc} onChange={(e) => setDesc(e.target.value)}
                        className="w-full flex min-h-[80px] rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
                    <Button type="submit" isLoading={loading}>Create</Button>
                </div>
            </form>
        </Modal>
    );
}
