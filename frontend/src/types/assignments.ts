/**
 * AssignMind — Assignment Types
 */

export interface AssignmentSummary {
    requirements: string[];
    constraints: string[];
    deliverables: string[];
    deadlines: string[];
    tools: string[];
}

export interface AssignmentResponse {
    id: string;
    workspace_id: string;
    version: number;
    original_filename: string;
    file_url: string | null;
    structured_summary: AssignmentSummary;
    detected_language: string;
    uploaded_by: string;
    created_at: string;
}
