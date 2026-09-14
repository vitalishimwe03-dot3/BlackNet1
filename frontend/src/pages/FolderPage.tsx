import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { files as filesApi } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { formatBytes } from "../utils/format";

export function FolderPage() {
  const { folderId } = useParams<{ folderId: string }>();

  const { data } = useQuery({
    queryKey: ["files", "folder", folderId],
    queryFn: () => filesApi.list({ folder: folderId, page_size: 100 }).then((r) => r.data),
  });

  const list = data?.results ?? [];

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader
        title="FOLDER // VIEW"
        subtitle="STORAGE://USER"
        action={<Link to="/files" className="font-mono text-xs text-secondary hover:underline">← ALL FILES</Link>}
      />

      <TerminalCard title="CONTENTS" accent="primary">
        {list.length === 0 ? (
          <EmptyState icon="▣" title="EMPTY FOLDER" />
        ) : (
          <ul className="divide-y divide-borderline">
            {list.map((f) => (
              <li key={f.id} className="flex items-center justify-between gap-3 py-2.5">
                <span className="font-mono text-xs text-gray-200 truncate">{f.original_name}</span>
                <span className="flex items-center gap-3 font-mono text-[10px] text-muted shrink-0">
                  {formatBytes(f.size_bytes)}
                  {f.url && (
                    <a href={f.url} target="_blank" rel="noreferrer" className="text-secondary hover:underline">
                      PREVIEW
                    </a>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
      </TerminalCard>
    </div>
  );
}