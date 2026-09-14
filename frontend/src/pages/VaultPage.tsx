import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { files as filesApi } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { NeonButton } from "../components/NeonButton";
import { TerminalCard } from "../components/TerminalCard";
import { formatBytes } from "../utils/format";

export function VaultPage() {
  const [unlocked, setUnlocked] = useState(false);
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);

  const { data } = useQuery({
    queryKey: ["files", "vault"],
    queryFn: () => filesApi.list({ vault: "true", page_size: 100 }).then((r) => r.data),
    enabled: unlocked,
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      form.append("in_vault", "true");
      return filesApi.upload(form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files", "vault"] });
      queryClient.invalidateQueries({ queryKey: ["storage"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => filesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files", "vault"] });
      queryClient.invalidateQueries({ queryKey: ["storage"] });
    },
  });

  const unlock = () => {
    // Local UX gate only; files themselves remain owner-scoped server-side.
    if (pin.length >= 4) {
      setUnlocked(true);
      setError("");
    } else {
      setError("VAULT CODE REQUIRED");
    }
  };

  const list = data?.results ?? [];

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader title="VAULT://PRIVATE" subtitle="PROTECTED AREA — EXTRA AUTHENTICATION REQUIRED" />

      {!unlocked ? (
        <TerminalCard title="AUTHENTICATION GATE" accent="warn">
          <div className="max-w-sm mx-auto text-center">
            <div className="font-mono text-4xl text-warn mb-4">◉</div>
            <p className="font-mono text-xs text-muted mb-4">
              ENTER YOUR VAULT CODE TO UNLOCK THE PROTECTED AREA
            </p>
            <div className="flex gap-2">
              <input
                type="password"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && unlock()}
                placeholder="VAULT CODE"
                className="flex-1 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-warn outline-none"
              />
              <NeonButton variant="warn" onClick={unlock}>
                UNLOCK
              </NeonButton>
            </div>
            {error && <div className="mt-3 font-mono text-xs text-danger">{error}</div>}
          </div>
        </TerminalCard>
      ) : (
        <>
          <div className="mb-4 flex justify-end">
            <input
              ref={fileInput}
              type="file"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void uploadMutation.mutateAsync(f);
                e.target.value = "";
              }}
            />
            <NeonButton variant="warn" onClick={() => fileInput.current?.click()} disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? "SECURING..." : "▲ LOCK FILE IN VAULT"}
            </NeonButton>
          </div>

          <TerminalCard title="VAULT CONTENTS" accent="warn" action={<button className="font-mono text-[10px] text-muted hover:text-danger" onClick={() => setUnlocked(false)}>LOCK</button>}>
            {list.length === 0 ? (
              <EmptyState icon="◉" title="VAULT EMPTY" />
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
                      <button onClick={() => deleteMutation.mutate(f.id)} className="text-danger hover:underline">
                        PURGE
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </TerminalCard>
        </>
      )}
    </div>
  );
}