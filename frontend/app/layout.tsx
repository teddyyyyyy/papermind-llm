import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Papermind — Research Paper Q&A",
  description: "Upload research papers and ask questions with AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full`}>
      <body className="min-h-full bg-gray-50 text-gray-900 antialiased" suppressHydrationWarning>
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-4xl px-4 py-4 flex items-center gap-3">
            <span className="text-2xl">📄</span>
            <div>
              <h1 className="text-lg font-bold leading-none">Papermind</h1>
              <p className="text-xs text-gray-500">Research Paper Q&A</p>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
