/**
 * AssignMind — Modal Component
 *
 * Accessible dialog with backdrop, Escape key, and scroll lock.
 */

"use client";

import { useEffect, useCallback, type ReactNode } from "react";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
    const onKeyDown = useCallback(
        (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); },
        [onClose]
    );

    useEffect(() => {
        if (!isOpen) return;
        document.addEventListener("keydown", onKeyDown);
        document.body.style.overflow = "hidden";
        return () => { document.removeEventListener("keydown", onKeyDown); document.body.style.overflow = ""; };
    }, [isOpen, onKeyDown]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
            <div role="dialog" aria-modal="true" aria-labelledby="modal-title"
                className="relative z-10 w-full max-w-lg rounded-2xl bg-surface border border-border p-6 shadow-2xl animate-[scaleIn_0.2s_ease-out]">
                <div className="flex items-center justify-between mb-4">
                    <h2 id="modal-title" className="text-lg font-semibold text-foreground">{title}</h2>
                    <button onClick={onClose} className="text-muted hover:text-foreground p-1" aria-label="Close">
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                {children}
            </div>
        </div>
    );
}
