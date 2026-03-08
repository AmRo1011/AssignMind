/**
 * AssignMind — Tasks Types
 */

export interface TaskResponse {
    id: string;
    workspace_id: string;
    title: string;
    description: string | null;
    status: string;
    assigned_to: string | null;
    deadline: string | null;
    position: number;
    is_ai_generated: boolean;
    created_by: string;
    created_at: string;
    updated_at: string;
}

export interface TaskCreate {
    title: string;
    description?: string | null;
    status: string;
    assigned_to?: string | null;
    deadline?: string | null;
    is_ai_generated: boolean;
}

export interface GeneratedTaskResponse {
    title: string;
    description: string;
    assigned_to?: string | null;
}
