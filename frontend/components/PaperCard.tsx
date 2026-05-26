"use client";

import Link from "next/link";
import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import type { Job } from "@/lib/api";
import StatusBadge from "./StatusBadge";

interface Props {
  job: Job;
  onDelete: (job: Job) => void;
  deleting: boolean;
}

export default function PaperCard({ job, onDelete, deleting }: Props) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: job.id,
    data: { job },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.4 : 1,
    zIndex: isDragging ? 50 : undefined,
  };

  const displayTitle = job.title || job.filename;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="group relative flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm hover:border-blue-300 hover:shadow transition-all cursor-grab active:cursor-grabbing"
    >
      {/* Drag handle */}
      <span
        {...listeners}
        {...attributes}
        className="shrink-0 text-gray-300 hover:text-gray-500 cursor-grab active:cursor-grabbing select-none"
        title="Drag to move"
      >
        ⠿
      </span>

      {/* Content — click to navigate */}
      <Link
        href={`/jobs/${job.id}`}
        className="flex-1 min-w-0"
        onClick={(e) => isDragging && e.preventDefault()}
      >
        <p className="text-sm font-medium text-gray-800 truncate group-hover:text-blue-600">
          {displayTitle}
        </p>
        {job.title && (
          <p className="text-xs text-gray-400 truncate">{job.filename}</p>
        )}
      </Link>

      <StatusBadge status={job.status} />

      {/* Delete button */}
      <button
        onClick={(e) => { e.stopPropagation(); onDelete(job); }}
        disabled={deleting}
        title="Delete"
        className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-500 p-1 rounded disabled:opacity-30"
      >
        {deleting ? "⏳" : "🗑️"}
      </button>
    </div>
  );
}
