"use client";

import { useEffect, useState, useCallback } from "react";
import { DndContext, DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import {
  getJobs,
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  updateJob,
  deleteJob,
  type Job,
  type Category,
} from "@/lib/api";

import CategorySection from "./CategorySection";

const COLORS = [
  "#6366f1", // indigo
  "#ec4899", // pink
  "#f59e0b", // amber
  "#10b981", // emerald
  "#3b82f6", // blue
  "#f97316", // orange
  "#8b5cf6", // violet
  "#14b8a6", // teal
];

export default function CategoryBoard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<number | null>(null);
  const [newCatName, setNewCatName] = useState("");
  const [addingCat, setAddingCat] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  const load = useCallback(async () => {
    try {
      const [j, c] = await Promise.all([getJobs(), getCategories()]);
      setJobs(j.sort((a, b) => b.id - a.id));
      setCategories(c);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Drag end ────────────────────────────────────────────────────────────────
  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const jobId = Number(active.id);
    const targetId = String(over.id); // "cat-{id}" or "uncategorized"

    const newCategoryId = targetId === "uncategorized"
      ? null
      : parseInt(targetId.replace("cat-", ""), 10);

    const job = jobs.find((j) => j.id === jobId);
    if (!job || job.category_id === newCategoryId) return;

    // Optimistic update
    setJobs((prev) =>
      prev.map((j) => j.id === jobId ? { ...j, category_id: newCategoryId } : j)
    );

    try {
      await updateJob(jobId, { category_id: newCategoryId });
    } catch {
      // Rollback
      setJobs((prev) =>
        prev.map((j) => j.id === jobId ? { ...j, category_id: job.category_id } : j)
      );
    }
  };

  // ── Add category ────────────────────────────────────────────────────────────
  const handleAddCategory = async () => {
    const name = newCatName.trim();
    if (!name) return;
    const color = COLORS[categories.length % COLORS.length];
    try {
      const cat = await createCategory(name, color);
      setCategories((prev) => [...prev, cat]);
      setNewCatName("");
      setAddingCat(false);
    } catch {
      alert("Failed to create category");
    }
  };

  // ── Rename category ─────────────────────────────────────────────────────────
  const handleRename = async (id: number, name: string) => {
    try {
      const updated = await updateCategory(id, { name });
      setCategories((prev) => prev.map((c) => c.id === id ? updated : c));
    } catch {
      alert("Failed to rename category");
    }
  };

  // ── Delete category ─────────────────────────────────────────────────────────
  const handleDeleteCategory = async (id: number) => {
    const cat = categories.find((c) => c.id === id);
    if (!confirm(`Delete category "${cat?.name}"? Papers will move to Uncategorized.`)) return;
    try {
      await deleteCategory(id);
      setCategories((prev) => prev.filter((c) => c.id !== id));
      setJobs((prev) => prev.map((j) => j.category_id === id ? { ...j, category_id: null } : j));
    } catch {
      alert("Failed to delete category");
    }
  };

  // ── Delete job ───────────────────────────────────────────────────────────────
  const handleDeleteJob = async (job: Job) => {
    if (!confirm(`Delete "${job.title || job.filename}"?`)) return;
    setDeletingJobId(job.id);
    try {
      await deleteJob(job.id);
      setJobs((prev) => prev.filter((j) => j.id !== job.id));
    } catch {
      alert("Failed to delete paper");
    } finally {
      setDeletingJobId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="h-24 rounded-xl bg-gray-100 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">
        ⚠️ {error} — is the backend running?
      </p>
    );
  }

  const uncategorized = jobs.filter((j) => j.category_id === null);

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <div className="space-y-4">
        {/* Categories */}
        {categories.map((cat) => (
          <CategorySection
            key={cat.id}
            category={cat}
            jobs={jobs.filter((j) => j.category_id === cat.id)}
            onRename={handleRename}
            onDelete={handleDeleteCategory}
            onDeleteJob={handleDeleteJob}
            deletingJobId={deletingJobId}
          />
        ))}

        {/* Uncategorized section — always last */}
        <CategorySection
          category={null}
          jobs={uncategorized}
          onRename={() => {}}
          onDelete={() => {}}
          onDeleteJob={handleDeleteJob}
          deletingJobId={deletingJobId}
        />

        {/* Add category */}
        {addingCat ? (
          <div className="flex gap-2">
            <input
              autoFocus
              value={newCatName}
              onChange={(e) => setNewCatName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAddCategory();
                if (e.key === "Escape") { setAddingCat(false); setNewCatName(""); }
              }}
              placeholder="Category name…"
              className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            />
            <button
              onClick={handleAddCategory}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
            >
              Add
            </button>
            <button
              onClick={() => { setAddingCat(false); setNewCatName(""); }}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-500 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setAddingCat(true)}
            className="w-full rounded-xl border-2 border-dashed border-gray-200 py-3 text-sm text-gray-400 hover:border-gray-300 hover:text-gray-500 transition-colors"
          >
            + New Category
          </button>
        )}
      </div>
    </DndContext>
  );
}
