import type { Job } from "@/lib/api";

const styles: Record<Job["status"], string> = {
  pending: "bg-yellow-100 text-yellow-800",
  running: "bg-blue-100 text-blue-800",
  finished: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

const icons: Record<Job["status"], string> = {
  pending: "⏳",
  running: "⚙️",
  finished: "✅",
  failed: "❌",
};

export default function StatusBadge({ status }: { status: Job["status"] }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}
    >
      {icons[status]} {status}
    </span>
  );
}
