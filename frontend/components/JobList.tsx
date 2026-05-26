"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getJobs, deleteJob, type Job } from "@/lib/api";
import StatusBadge from "./StatusBadge";

export default function JobList() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    getJobs()
      .then((data) => setJobs(data.sort((a, b) => b.id - a.id)))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (e: React.MouseEvent, job: Job) => {
    e.preventDefault(); // prevent Link navigation
    if (!confirm(`Delete "${job.filename}"?`)) return;
    setDeletingId(job.id);
    try {
      await deleteJob(job.id);
      setJobs((prev) => prev.filter((j) => j.id !== job.id));
    } catch {
      alert("Failed to delete — please try again.");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-lg bg-gray-100 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">
        ⚠️ Could not load jobs — is the backend running?
      </p>
    );
  }

  if (jobs.length === 0) {
    return (
      <p className="text-sm text-gray-400 text-center py-6">
        No papers uploaded yet. Upload one above to get started.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {jobs.map((job) => (
        <div key={job.id} className="relative group">
          <Link
            href={`/jobs/${job.id}`}
            className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3 hover:border-blue-300 hover:shadow-sm transition-all pr-12"
          >
            <div className="flex items-center gap-3 min-w-0">
              <span className="text-xl shrink-0">📄</span>
              <div className="min-w-0">
                <p className="text-sm font-medium truncate group-hover:text-blue-600">
                  {job.filename}
                </p>
                <p className="text-xs text-gray-400">
                  {new Date(job.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
            <StatusBadge status={job.status} />
          </Link>

          {/* Delete button — sits on top of the link */}
          <button
            onClick={(e) => handleDelete(e, job)}
            disabled={deletingId === job.id}
            title="Delete paper"
            className="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity rounded-md p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 disabled:opacity-40"
          >
            {deletingId === job.id ? "⏳" : "🗑️"}
          </button>
        </div>
      ))}
    </div>
  );
}
