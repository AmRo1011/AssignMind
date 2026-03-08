"use client";

import { useEffect, useState, useRef, use } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useToast } from "@/providers/ToastProvider";
import { Spinner } from "@/components/ui/Spinner";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import type { WorkspaceResponse } from "@/types/workspaces";
import type { ChatMessageResponse } from "@/types/chat";

export default function ChatPage({ params }: { params: Promise<{ workspaceId: string }> }) {
    const { workspaceId } = use(params);
    const { user } = useCurrentUser();
    const router = useRouter();
    const { addToast } = useToast();

    const [ws, setWs] = useState<WorkspaceResponse | null>(null);
    const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [content, setContent] = useState("");

    // Pagination
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);

    const LIMIT = 50;
    const pollingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const fetchMessages = async (currentOffset: number, append: boolean = false) => {
        try {
            const data = await apiGet<ChatMessageResponse[]>(`/workspaces/${workspaceId}/chat?limit=${LIMIT}&offset=${currentOffset}`);
            if (data.length < LIMIT) setHasMore(false);

            setMessages(prev => append ? [...prev, ...data] : data);
            return data;
        } catch (err: any) {
            if (err.status === 403 || err.status === 404) router.push("/dashboard");
            return [];
        }
    };

    const loadInitialData = async () => {
        setLoading(true);
        try {
            const [wData] = await Promise.all([
                apiGet<WorkspaceResponse>(`/workspaces/${workspaceId}`),
                fetchMessages(0, false)
            ]);
            setWs(wData);
        } catch (err: any) {
            addToast("error", "Failed to load chat data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadInitialData();
        return () => stopPolling();
    }, [workspaceId]);

    const startPolling = () => {
        stopPolling();
        pollingTimeoutRef.current = setTimeout(async () => {
            if (offset === 0) {
                await fetchMessages(0, false);
            }
            startPolling();
        }, 30000);
    };

    const stopPolling = () => {
        if (pollingTimeoutRef.current) clearTimeout(pollingTimeoutRef.current);
    };

    useEffect(() => {
        startPolling();
        return () => stopPolling();
    }, [offset]); // Re-bind when offset changes (though we only poll if offset 0)

    const handleLoadMore = async () => {
        if (loadingMore || !hasMore) return;
        setLoadingMore(true);
        const nextOffset = offset + LIMIT;
        await fetchMessages(nextOffset, true);
        setOffset(nextOffset);
        setLoadingMore(false);
    };

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        // Due to flex-col-reverse, scrollTop starts at 0 at bottom, and goes negative (or positive depending on browser).
        // Standard check:
        const t = e.currentTarget;
        // In flex-col-reverse, scrolling "up" towards older messages means reaching the top of the container.
        // Some browsers do reverse scroll differently, but usually `scrollTop` approaches `-(scrollHeight - clientHeight)` or just increases if standard.
        // A safer cross-browser way is checking close to top:
        if (Math.abs(t.scrollTop) + t.clientHeight >= t.scrollHeight - 50) {
            handleLoadMore();
        }
    };

    const handleSend = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!content.trim() || sending) return;

        setSending(true);
        try {
            await apiPost(`/workspaces/${workspaceId}/chat`, { content });
            setContent("");
            // Reset offset and fetch latest
            setOffset(0);
            setHasMore(true);
            await fetchMessages(0, false);
        } catch (err: any) {
            addToast("error", err.message || "Failed to send message.");
        } finally {
            setSending(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (loading || !ws) {
        return <div className="p-12 center flex justify-center"><Spinner size="lg" /></div>;
    }

    return (
        <div className="max-w-[1000px] mx-auto p-4 md:p-8 h-[calc(100vh-80px)] flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)]">Smart Chat</h1>
                    <p className="text-muted text-sm mt-1">{ws.title} — Collaborate alongside the Supervisor AI.</p>
                </div>
            </div>

            <div
                className="flex-1 border bg-surface rounded-2xl overflow-y-auto flex flex-col-reverse p-4 gap-4"
                onScroll={handleScroll}
            >
                {messages.map((m) => {
                    const isSupervisor = m.sender_type === "supervisor" || m.sender_type === "agent";
                    const isMe = m.sender_id === user?.id;
                    const avatarSrc = isSupervisor ? null : (ws.members?.find(mem => mem.user_id === m.sender_id)?.user?.avatar_url || null);

                    return (
                        <div key={m.id} className={`flex max-w-[80%] gap-3 ${isMe ? "self-end flex-row-reverse" : "self-start"}`}>
                            {!isMe && (
                                <Avatar
                                    src={avatarSrc}
                                    name={isSupervisor ? "Supervisor" : m.sender_name}
                                    size="md"
                                    className="flex-shrink-0 mt-1"
                                />
                            )}
                            <div className={`flex flex-col gap-1 ${isMe ? "items-end" : "items-start"}`}>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-xs font-semibold text-foreground">
                                        {isSupervisor ? "🤖 Supervisor Agent" : (isMe ? "You" : m.sender_name)}
                                    </span>
                                    <span className="text-[10px] text-muted">
                                        {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                                <div
                                    className={`px-4 py-2 text-sm rounded-2xl whitespace-pre-wrap ${isSupervisor
                                            ? "bg-primary/10 border border-primary/20 text-foreground rounded-tl-sm shadow-sm"
                                            : isMe
                                                ? "bg-primary text-white rounded-tr-sm shadow-md"
                                                : "bg-muted/10 border border-border text-foreground rounded-tl-sm shadow-sm"
                                        }`}
                                >
                                    {m.content}
                                </div>
                            </div>
                        </div>
                    );
                })}

                {loadingMore && <div className="py-4 flex justify-center"><Spinner size="sm" /></div>}
                {!loadingMore && !hasMore && messages.length > 0 && (
                    <div className="py-4 text-center text-xs text-muted">Beginning of chat history</div>
                )}
                {messages.length === 0 && !loadingMore && (
                    <div className="my-auto text-center text-muted">No messages yet. Send a message to start!</div>
                )}
            </div>

            <div className="mt-4 bg-surface border rounded-xl p-2 flex gap-2 shadow-sm">
                <textarea
                    className="flex-1 bg-transparent border-none focus:ring-0 resize-none max-h-32 min-h-[44px] p-2 text-sm outline-none"
                    placeholder="Type a message (Shift+Enter for newline)..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={sending}
                    rows={1}
                />
                <Button
                    className="self-end mb-0.5"
                    onClick={handleSend}
                    isLoading={sending}
                    disabled={!content.trim()}
                >
                    Send
                </Button>
            </div>
        </div>
    );
}
