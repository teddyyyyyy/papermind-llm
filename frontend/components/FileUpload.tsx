"use client";

import { useState, useCallback, DragEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { uploadFile } from "@/lib/api";

export default function FileUpload() {
  const router = useRouter();
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.match(/\.(pdf|txt)$/i)) {
        setError("Only PDF and TXT files are supported.");
        return;
      }
      setError(null);
      setUploading(true);
      try {
        const job = await uploadFile(file);
        router.push(`/jobs/${job.id}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
        setUploading(false);
      }
    },
    [router]
  );

  const onDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleUpload(file);
    },
    [handleUpload]
  );

  const onFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleUpload(file);
    },
    [handleUpload]
  );

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 transition-colors cursor-pointer
          ${dragging ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50"}
          ${uploading ? "opacity-60 pointer-events-none" : ""}
        `}
      >
        <input
          type="file"
          accept=".pdf,.txt"
          className="absolute inset-0 opacity-0 cursor-pointer"
          onChange={onFileChange}
          disabled={uploading}
        />
        <div className="text-5xl mb-3">{uploading ? "⏳" : "📂"}</div>
        <p className="text-sm font-medium text-gray-700">
          {uploading ? "Uploading…" : "Drag & drop a PDF or TXT file here"}
        </p>
        <p className="mt-1 text-xs text-gray-400">or click to browse</p>
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600 bg-red-50 rounded px-3 py-2">
          ⚠️ {error}
        </p>
      )}
    </div>
  );
}
