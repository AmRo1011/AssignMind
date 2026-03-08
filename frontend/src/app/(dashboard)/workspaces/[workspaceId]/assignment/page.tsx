import ClientPage from "./ClientPage";

export function generateStaticParams() {
    return [{ workspaceId: "[workspaceId]" }];
}

export default async function Page(props: { params: Promise<{ workspaceId: string }> }) {
    const params = await props.params;
    return <ClientPage workspaceId={params.workspaceId} />;
}
