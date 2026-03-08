import type { AssignmentSummary } from "@/types/assignments";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

export default function AssignmentSummaryCard({ summary, version }: { summary: AssignmentSummary, version: number }) {

    const renderList = (items: string[], emptyMsg: string) => {
        if (!items || items.length === 0) return <p className="text-sm text-muted italic">{emptyMsg}</p>;
        return (
            <ul className="list-disc pl-5 text-sm space-y-1">
                {items.map((item, id) => <li key={id}>{item}</li>)}
            </ul>
        );
    };

    return (
        <Card className="p-6 space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
                <h2 className="text-xl font-bold font-[family-name:var(--font-outfit)]">Assignment Breakdown</h2>
                <Badge variant="success">Version {version}</Badge>
            </div>

            <div>
                <h3 className="font-semibold text-lg text-primary mb-2">Key Requirements</h3>
                {renderList(summary.requirements, "No explicit requirements detected.")}
            </div>

            <div>
                <h3 className="font-semibold text-lg text-destructive mb-2">Constraints & Gotchas</h3>
                {renderList(summary.constraints, "No specific constraints found.")}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 className="font-semibold text-md mb-2">Expected Deliverables</h3>
                    {renderList(summary.deliverables, "No explicit deliverables detected.")}
                </div>
                <div>
                    <h3 className="font-semibold text-md mb-2">Tools & Ecosystem</h3>
                    {renderList(summary.tools, "No specific tools required.")}
                </div>
            </div>

            {summary.deadlines?.length > 0 && (
                <div className="bg-destructive/10 p-3 rounded-md">
                    <h3 className="font-semibold text-destructive mb-1 text-sm">Deadlines Detected</h3>
                    {renderList(summary.deadlines, "")}
                </div>
            )}
        </Card>
    );
}
