import FileUpload from "@/components/FileUpload";
import CategoryBoard from "@/components/CategoryBoard";

export default function HomePage() {
  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Upload a Research Paper</h2>
        <p className="text-gray-500 text-sm">
          Drop a PDF or TXT file and ask questions about it using AI
        </p>
      </div>

      {/* Upload */}
      <FileUpload />

      {/* Category board */}
      <div>
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          My Papers
        </h3>
        <CategoryBoard />
      </div>
    </div>
  );
}
