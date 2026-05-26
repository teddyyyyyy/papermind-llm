const BASE = "/api";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Job {
  id: number;
  filename: string;
  title: string | null;
  status: "pending" | "running" | "finished" | "failed";
  summary: string | null;
  category_id: number | null;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  color: string;
  created_at: string;
}

export interface AskResponse {
  job_id: number;
  question: string;
  answer: string;
}

// ─── Jobs ─────────────────────────────────────────────────────────────────────

export async function uploadFile(file: File): Promise<Job> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/jobs`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJobs(): Promise<Job[]> {
  const res = await fetch(`${BASE}/jobs`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJob(id: number): Promise<Job> {
  const res = await fetch(`${BASE}/jobs/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateJob(id: number, patch: { category_id: number | null }): Promise<Job> {
  const res = await fetch(`${BASE}/jobs/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteJob(id: number): Promise<void> {
  const res = await fetch(`${BASE}/jobs/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
}

export async function askQuestion(
  jobId: number,
  question: string
): Promise<AskResponse> {
  const res = await fetch(`${BASE}/jobs/${jobId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ─── Categories ───────────────────────────────────────────────────────────────

export async function getCategories(): Promise<Category[]> {
  const res = await fetch(`${BASE}/categories`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createCategory(name: string, color?: string): Promise<Category> {
  const res = await fetch(`${BASE}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, color: color ?? "#6366f1" }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateCategory(
  id: number,
  patch: { name?: string; color?: string }
): Promise<Category> {
  const res = await fetch(`${BASE}/categories/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteCategory(id: number): Promise<void> {
  const res = await fetch(`${BASE}/categories/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
}
