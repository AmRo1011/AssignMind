/**
 * AssignMind — Workspace & Invitation Types
 */
import type { UserResponse } from "./user";

export interface WorkspaceMemberResponse {
    id: string;
    workspace_id: string;
    user_id: string;
    role: string;
    joined_at: string;
    user?: UserResponse;
}

export interface WorkspaceResponse {
    id: string;
    title: string;
    description: string | null;
    deadline: string | null;
    is_archived: boolean;
    archived_at: string | null;
    created_by: string;
    created_at: string;
    updated_at: string;
    members?: WorkspaceMemberResponse[];
    role?: string;
}

export interface MinimalWorkspace {
    id: string;
    title: string;
}

export interface InvitationResponse {
    id: string;
    workspace_id: string;
    email: string;
    invited_by: string;
    status: string;
    created_at: string;
    responded_at: string | null;
}

export interface InvitationWithWorkspaceResponse extends InvitationResponse {
    workspace?: MinimalWorkspace;
}
