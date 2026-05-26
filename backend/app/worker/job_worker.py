import re
import time
import traceback

from pathlib import Path

from openai import OpenAI

from pypdf import PdfReader

from app.config.database import SessionLocal

from app.models.inference_job import InferenceJob

from app.services.rag_service import store_chunks


client = OpenAI()

LLM_MODEL = "gpt-5.4-mini"

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"

# Max characters sent to the LLM for title+summary (~3000 tokens)
# The full text is still used for chunking/embedding
SUMMARY_MAX_CHARS = 12_000


def process_jobs():

    while True:

        db = SessionLocal()

        pending_jobs = db.query(InferenceJob).filter(
            InferenceJob.status == "pending"
        ).all()

        for job in pending_jobs:

            print(f"[worker] Processing job {job.id} — {job.filename}")

            job.status = "running"
            db.commit()

            try:
                file_path = UPLOAD_DIR / job.filename

                # ── Step 1: Read file ────────────────────────────────────────
                if file_path.suffix.lower() == ".pdf":
                    reader = PdfReader(file_path)
                    text = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()

                # Strip NUL bytes — PostgreSQL rejects \x00 in text columns
                text = text.replace("\x00", "")
                print(f"[worker] Read {len(text):,} characters from {job.filename}")

                # ── Step 2: Title + summary (truncated text only) ────────────
                # Truncate to avoid context-window errors and slow responses
                text_for_llm = text[:SUMMARY_MAX_CHARS]
                if len(text) > SUMMARY_MAX_CHARS:
                    text_for_llm += "\n\n[Document truncated for summary — full text used for Q&A]"

                print(f"[worker] Requesting title+summary from LLM...")
                response = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are analyzing a research paper or document.

1. Extract or infer the title. If it's a research paper, use the actual title. Otherwise create a short descriptive title (max 10 words).
2. Write a clear, concise summary (3-5 sentences).

Respond in exactly this format:
TITLE: <title here>
SUMMARY: <summary here>

Document:
{text_for_llm}
"""
                        }
                    ],
                    timeout=60,  # don't wait more than 60s
                )

                content = response.choices[0].message.content or ""
                print(f"[worker] LLM raw response: {content[:300]}")

                # Robust parsing with regex — handles varied LLM formatting
                title = job.filename   # fallback
                summary = content      # fallback

                title_match = re.search(r"TITLE:\s*(.+?)(?=\nSUMMARY:|\Z)", content, re.DOTALL)
                summary_match = re.search(r"SUMMARY:\s*(.+)", content, re.DOTALL)

                if title_match:
                    title = title_match.group(1).strip()
                    print(f"[worker] Parsed title: {title}")
                else:
                    print(f"[worker] ⚠️ Could not parse TITLE from response")

                if summary_match:
                    summary = summary_match.group(1).strip()
                else:
                    print(f"[worker] ⚠️ Could not parse SUMMARY from response")

                job.title = title
                job.summary = summary
                db.commit()
                print(f"[worker] Title: {title}")

                # ── Step 3: Chunk + batch-embed full text ────────────────────
                store_chunks(db, job.id, text)

                job.status = "finished"
                db.commit()
                print(f"[worker] ✅ Finished job {job.id}")

            except Exception as e:
                traceback.print_exc()
                try:
                    db.rollback()   # reset broken session before writing
                    job.status = "failed"
                    db.commit()
                    print(f"[worker] ❌ Job {job.id} marked as failed")
                except Exception as inner:
                    print(f"[worker] ❌ Could not mark job as failed: {inner}")
                    db.rollback()

        db.close()
        time.sleep(1)


if __name__ == "__main__":
    process_jobs()
