"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getJob, deleteJob, type Job } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";
import QAInterface from "@/components/QAInterface";

export default function JobPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = Number(params.id);

  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchJob = useCallback(async () => {
    try {
      const data = await getJob(jobId);
      setJob(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load job");
    }
  }, [jobId]);

  useEffect(() => {
    fetchJob();
  }, [fetchJob]);

  useEffect(() => {
    if (!job || job.status === "finished" || job.status === "failed") return;
    const interval = setInterval(fetchJob, 3000);
    return () => clearInterval(interval);
  }, [job, fetchJob]);

  const handleDelete = async () => {
    if (!job || !confirm(`Delete "${job.filename}"?`)) return;
    setDeleting(true);
    try {
      await deleteJob(job.id);
      router.push("/");
    } catch {
      alert("Failed to delete — please try again.");
      setDeleting(false);
    }
  };

  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          ← Back
        </Link>
        <p className="text-red-600 bg-red-50 rounded px-3 py-2 text-sm">
          ⚠️ {error}
        </p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-4 w-16 rounded bg-gray-200" />
        <div className="h-8 w-64 rounded bg-gray-200" />
        <div className="h-32 rounded-xl bg-gray-200" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back + header */}
      <div>
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          ← Back to all papers
        </Link>
        <div className="mt-3 flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-2xl font-bold truncate">{job.filename}</h2>
            <p className="text-xs text-gray-400 mt-1">
              Uploaded{" "}
              {new Date(job.created_at).toLocaleDateString(undefined, {
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <StatusBadge status={job.status} />
            <button
              onClick={handleDelete}
              disabled={deleting}
              title="Delete this paper"
              className="rounded-md px-3 py-1.5 text-sm text-red-500 border border-red-200 hover:bg-red-50 disabled:opacity-40 transition-colors"
            >
              {deleting ? "Deleting…" : "🗑️ Delete"}
            </button>
          </div>
        </div>
      </div>

      {/* Processing state */}
      {(job.status === "pending" || job.status === "running") && (
        <div className="rounded-xl bg-blue-50 border border-blue-200 px-5 py-4 flex items-center gap-3">
          <span className="text-2xl animate-spin">⚙️</span>
          <div>
            <p className="text-sm font-medium text-blue-800">
              {job.status === "pending"
                ? "Queued for processing…"
                : "Chunking and embedding the paper…"}
            </p>
            <p className="text-xs text-blue-600 mt-0.5">
              This usually takes 15–60 seconds. This page auto-refreshes.
            </p>
          </div>
        </div>
      )}

      {/* Failed state */}
      {job.status === "failed" && (
        <div className="rounded-xl bg-red-50 border border-red-200 px-5 py-4">
          <p className="text-sm font-medium text-red-800">
            ❌ Processing failed. Try uploading the file again.
          </p>
        </div>
      )}

      {/* Summary */}
      {job.status === "finished" && job.summary && (
        <div className="rounded-xl bg-white border border-gray-200 px-5 py-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Summary
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {job.summary}
          </p>
        </div>
      )}

      {/* Q&A */}
      {job.status === "finished" && (
        <div className="rounded-xl bg-gray-50 border border-gray-200 px-5 py-5">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Ask a Question
          </h3>
          <QAInterface jobId={job.id} />
        </div>
      )}
    </div>
  );
}
