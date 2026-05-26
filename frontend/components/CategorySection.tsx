"use client";

import { useState, useRef, useEffect } from "react";
import { useDroppable } from "@dnd-kit/core";
import type { Job, Category } from "@/lib/api";
import PaperCard from "./PaperCard";

const UNCATEGORIZED_LABEL_KEY = "uncategorized-label";

interface Props {
  category: Category | null; // null = "Uncategorized"
  jobs: Job[];
  onRename: (id: number, name: string) => void;
  onDelete: (id: number) => void;
  onDeleteJob: (job: Job) => void;
  deletingJobId: number | null;
}

export default function CategorySection({
  category,
  jobs,
  onRename,
  onDelete,
  onDeleteJob,
  deletingJobId,
}: Props) {
  const droppableId = category ? `cat-${category.id}` : "uncategorized";
  const { setNodeRef, isOver } = useDroppable({ id: droppableId });

  // For uncategorized, the display name lives in localStorage
  const [uncatLabel, setUncatLabel] = useState("Uncategorized");

  useEffect(() => {
    if (!category) {
      const saved = localStorage.getItem(UNCATEGORIZED_LABEL_KEY);
      if (saved) setUncatLabel(saved);
    }
  }, [category]);

  const [editing, setEditing] = useState(false);
  const [nameValue, setNameValue] = useState("");
  const [collapsed, setCollapsed] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Seed the input when editing starts
  const startEditing = () => {
    setNameValue(category ? category.name : uncatLabel);
    setEditing(true);
  };

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  const commitRename = () => {
    setEditing(false);
    const trimmed = nameValue.trim();
    if (!trimmed) return;

    if (category) {
      // Real category — call API
      if (trimmed !== category.name) onRename(category.id, trimmed);
    } else {
      // Uncategorized — persist in localStorage only
      setUncatLabel(trimmed);
      localStorage.setItem(UNCATEGORIZED_LABEL_KEY, trimmed);
    }
  };

  const displayName = category ? category.name : uncatLabel;
  const color = category?.color ?? "#9ca3af";

  return (
    <div
      ref={setNodeRef}
      className={`rounded-xl border-2 transition-colors ${
        isOver ? "border-blue-400 bg-blue-50" : "border-gray-200 bg-gray-50"
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3">
        <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color }} />

        {editing ? (
          <input
            ref={inputRef}
            value={nameValue}
            onChange={(e) => setNameValue(e.target.value)}
            onBlur={commitRename}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitRename();
              if (e.key === "Escape") setEditing(false);
            }}
            className="flex-1 text-sm font-semibold bg-white border border-blue-400 rounded px-2 py-0.5 outline-none focus:ring-2 focus:ring-blue-200"
          />
        ) : (
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="flex-1 text-left text-sm font-semibold text-gray-700 hover:text-gray-900"
          >
            {displayName}
            <span className="ml-2 text-xs font-normal text-gray-400">
              {collapsed ? `(${jobs.length} hidden)` : `(${jobs.length})`}
            </span>
          </button>
        )}

        {/* Actions */}
        {!editing && (
          <div className="flex items-center gap-1 shrink-0">
            <button
              onClick={startEditing}
              title="Rename"
              className="text-gray-400 hover:text-gray-600 p-1 rounded text-xs"
            >
              ✏️
            </button>
            {/* Delete only for real categories */}
            {category && (
              <button
                onClick={() => onDelete(category.id)}
                title="Delete category"
                className="text-gray-400 hover:text-red-500 p-1 rounded text-xs"
              >
                🗑️
              </button>
            )}
          </div>
        )}
      </div>

      {/* Job cards */}
      {!collapsed && (
        <div className="px-3 pb-3 space-y-2 min-h-[48px]">
          {jobs.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-3">
              {isOver ? "Drop here" : "No papers here — drag one in"}
            </p>
          ) : (
            jobs.map((job) => (
              <PaperCard
                key={job.id}
                job={job}
                onDelete={onDeleteJob}
                deleting={deletingJobId === job.id}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}
