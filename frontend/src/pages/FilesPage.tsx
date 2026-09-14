import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { files as filesApi } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { NeonButton } from "../components/NeonButton";
import { TerminalCard } from "../components/TerminalCard";
import { formatBytes } from "../utils/format";
import type { FileEntry } from "../types";
import { Link, useSearchParams } from "react-router-dom";

export function FilesPage() {
  const queryClient = useQueryClient();
  const [params] = useSearchParams();
  const autoUpload = params.get("action") === "upload";
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [shareInfo, setShareInfo] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["files"],
    queryFn: () => filesApi.list({ page_size: 50 }).then((r) => r.data),
  });

  const { data: folders } = useQuery({
    queryKey: ["folders"],
    queryFn: () => filesApi.folders({ page_size: 100 }).then((r) => r.data),
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return filesApi.upload(form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["storage"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => filesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["storage"] });
    },
  });

  const renameMutation = useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => filesApi.rename(id, name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["files"] }),
  });

  const moveMutation = useMutation({
    mutationFn: ({ id, folder }: { id: string; folder: string | null }) => filesApi.move(id, folder),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["files"] }),
  });

  const shareMutation = useMutation({
    mutationFn: (id: string) => filesApi.share(id, { expires_hours: 24 }),
    onSuccess: (r) => setShareInfo(r.data.url),
  });

  const onFile = async (file: File | undefined) => {
    if (!file) return;
    setUploading(true);
    try {
      await uploadMutation.mutateAsync(file);
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  const list = data?.results ?? [];

  return (
    <div className="max-w-5xl mx-auto">
      <PageHeader
        title="FILE EXPLORER"
        subtitle="STORAGE://USER — SORT, PREVIEWS, INDEXED METADATA"
        action={
          <>
            <input
              ref={fileInput}
              type="file"
              className="hidden"
              onChange={(e) => onFile(e.target.files?.[0])}
              data-testid="file-input"
            />
            <NeonButton onClick={() => fileInput.current?.click()} disabled={uploading}>
              {uploading ? "UPLOADING..." : "▲ UPLOAD FILE"}
            </NeonButton>
          </>
        }
      />

      {autoUpload && (
        <div className="mb-4 border border-secondary/40 bg-secondary/5 rounded-lg p-3 font-mono text-xs text-secondary">
          UPLOAD MODE: SELECT A FILE TO TRANSFER IT INTO YOUR QUOTA
        </div>
      )}

      {shareInfo && (
        <div className="mb-4 border border-primary/40 bg-primary/5 rounded-lg p-3 font-mono text-xs text-primary break-all">
          SHARE://LINK CREATED<br />
          {shareInfo} <button className="underline text-secondary" onClick={() => navigator.clipboard.writeText(shareInfo)}>COPY</button>
        </div>
      )}

      {/* Folders */}
      {(folders?.results ?? []).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {(folders?.results ?? []).map((folder) => (
            <Link
              key={folder.id}
              to={`/files/${folder.id}`}
              className="terminal-card rounded-lg p-3 hover:border-secondary/40 transition-colors"
            >
              <div className="text-secondary text-lg">▣</div>
              <div className="font-mono text-xs text-secondary mt-1 truncate">/{folder.name}</div>
              <div className="font-mono text-[10px] text-muted">{folder.file_count} FILES</div>
            </Link>
          ))}
        </div>
      )}

      <TerminalCard title="STORAGE VIEW" accent="cyan">
        {isLoading ? (
          <div className="font-mono text-xs text-muted blink">INDEXING...</div>
        ) : list.length === 0 ? (
          <div className="flex items-center justify-between">
            <EmptyState icon="▤" title="NO FILES" hint="UPLOAD YOUR FIRST FILE" />
          </div>
        ) : (
          <ul className="divide-y divide-borderline">
            {list.map((f) => (
              <FileRow
                key={f.id}
                file={f}
                folders={folders?.results ?? []}
                onDelete={() => deleteMutation.mutate(f.id)}
                onRename={(name) => renameMutation.mutate({ id: f.id, name })}
                onMove={(folder) => moveMutation.mutate({ id: f.id, folder })}
                onShare={() => shareMutation.mutate(f.id)}
              />
            ))}
          </ul>
        )}
      </TerminalCard>
    </div>
  );
}

function FileRow({ file, onDelete, onRename, onMove, onShare, folders }: {
  file: FileEntry;
  folders: { id: string; name: string; file_count: number }[];
  onDelete: () => void;
  onRename: (name: string) => void;
  onMove: (folder: string | null) => void;
  onShare: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(file.original_name);

  return (
    <li className="flex items-center gap-3 py-2.5 flex-wrap sm:flex-nowrap">
      <div className="w-9 h-9 shrink-0 rounded bg-panel2 border border-borderline flex items-center justify-center text-muted">
        {file.thumbnail_url ? (
          <img src={file.thumbnail_url} alt="" loading="lazy" className="w-full h-full object-cover rounded" />
        ) : (
          <span className="font-mono text-[10px]">{file.category.slice(0, 2).toUpperCase()}</span>
        )}
      </div>

      <div className="flex-1 min-w-0">
        {editing ? (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              onRename(name.trim() || file.original_name);
              setEditing(false);
            }}
            className="flex gap-2"
          >
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-panel2 border border-borderline rounded px-2 py-1 font-mono text-xs text-primary outline-none focus:border-primary w-full"
            />
            <button type="submit" className="font-mono text-[10px] text-primary">✓</button>
          </form>
        ) : (
          <div className="font-mono text-xs text-gray-200 truncate">{file.original_name}</div>
        )}
        <div className="font-mono text-[10px] text-muted">
          {formatBytes(file.size_bytes)} · {file.content_type}
        </div>
      </div>

      <div className="flex items-center gap-1 text-[11px] font-mono text-muted shrink-0 flex-wrap">
        {file.url && (
          <a href={file.url} target="_blank" rel="noreferrer" className="hover:text-primary">PREVIEW</a>
        )}
        {file.url && (
          <a href={file.url} download className="hover:text-secondary">DL</a>
        )}
        <button onClick={() => setEditing(!editing)} className="hover:text-warn">RENAME</button>
        <select
          defaultValue=""
          onChange={(e) => onMove(e.target.value === "__root__" ? null : e.target.value || null)}
          className="bg-panel2 border border-borderline rounded px-1 py-0.5 text-[10px] bg-panel2"
          aria-label="Move to folder"
        >
          <option value="">MOVE...</option>
          <option value="__root__">/ ROOT</option>
          {folders.filter((folder) => folder.id !== file.folder).map((folder) => (
            <option key={folder.id} value={folder.id}>
              / {folder.name}
            </option>
          ))}
        </select>
        <button onClick={onShare} className="hover:text-secondary">SHARE</button>
        <button onClick={onDelete} className="hover:text-danger">DEL</button>
      </div>
    </li>
  );
}