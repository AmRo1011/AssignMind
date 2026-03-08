"use client";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";

interface Props {
    isOpen: boolean;
    isLoading: boolean;
    onClose: () => void;
    onConfirm: () => void;
}

export function DangerZoneModal({ isOpen, isLoading, onClose, onConfirm }: Props) {
    return (
        <Modal isOpen={isOpen} onClose={() => !isLoading && onClose()} title="Are you absolutely sure?">
            <div className="flex flex-col gap-4 mt-2">
                <p className="text-sm text-muted">
                    This action will immediately <span className="text-foreground font-bold">deactivate</span> your account.
                </p>
                <ul className="list-disc text-sm text-error/90 pl-5 space-y-1">
                    <li>You will be logged out instantly.</li>
                    <li>Your account enters a 14-day grace period.</li>
                    <li>After 14 days, your data will be permanently deleted.</li>
                </ul>
                <div className="flex justify-end gap-3 mt-4">
                    <Button variant="ghost" onClick={onClose} disabled={isLoading}>Cancel</Button>
                    <Button variant="danger" onClick={onConfirm} isLoading={isLoading}>Yes, delete my account</Button>
                </div>
            </div>
        </Modal>
    );
}
