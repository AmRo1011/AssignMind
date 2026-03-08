/**
 * AssignMind — Chat Types
 */

export interface ChatMessageResponse {
    id: string;
    workspace_id: string;
    sender_id: string | null;
    sender_type: "human" | "supervisor" | string;
    sender_name: string;
    content: string;
    created_at: string;
}

export interface ChatMessageCreate {
    content: string;
}
