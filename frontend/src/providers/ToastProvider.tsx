"use client";

/**
 * AssignMind — Toast Notification Provider
 *
 * Lightweight toast system using React Context. No external
 * dependency — keeps bundle small for MVP.
 */

import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
} from "react";

type ToastType = "success" | "error" | "warning" | "info";

interface Toast {
    id: string;
    type: ToastType;
    message: string;
}

interface ToastContextValue {
    toasts: Toast[];
    addToast: (type: ToastType, message: string) => void;
    removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue>({
    toasts: [],
    addToast: () => { },
    removeToast: () => { },
});

interface ToastProviderProps {
    children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const addToast = useCallback(
        (type: ToastType, message: string) => {
            const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
            setToasts((prev) => [...prev, { id, type, message }]);

            // Auto-dismiss after 5 seconds
            setTimeout(() => removeToast(id), 5000);
        },
        [removeToast]
    );

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
            {children}
            <ToastContainer toasts={toasts} onDismiss={removeToast} />
        </ToastContext.Provider>
    );
}

/** Hook to access toast context. */
export function useToast(): ToastContextValue {
    return useContext(ToastContext);
}

/* ── Toast UI ── */

interface ToastContainerProps {
    toasts: Toast[];
    onDismiss: (id: string) => void;
}

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
    if (toasts.length === 0) return null;

    return (
        <div
            aria-live="polite"
            className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm"
        >
            {toasts.map((toast) => (
                <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
            ))}
        </div>
    );
}

interface ToastItemProps {
    toast: Toast;
    onDismiss: (id: string) => void;
}

const TOAST_STYLES: Record<ToastType, string> = {
    success: "bg-green-600 text-white",
    error: "bg-red-600 text-white",
    warning: "bg-amber-500 text-white",
    info: "bg-blue-600 text-white",
};

function ToastItem({ toast, onDismiss }: ToastItemProps) {
    return (
        <div
            role="alert"
            className={`${TOAST_STYLES[toast.type]} rounded-xl px-4 py-3 shadow-xl flex items-center gap-3 animate-[slideIn_0.3s_ease-out]`}
        >
            <span className="text-sm font-medium flex-1">{toast.message}</span>
            <button
                onClick={() => onDismiss(toast.id)}
                className="text-white/80 hover:text-white text-lg leading-none"
                aria-label="Dismiss notification"
            >
                ×
            </button>
        </div>
    );
}
