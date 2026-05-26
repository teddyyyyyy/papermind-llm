import time

from pathlib import Path

from openai import OpenAI

from pypdf import PdfReader

from app.config.database import SessionLocal

from app.models.inference_job import InferenceJob

from app.services.rag_service import store_chunks


client = OpenAI()  # reads OPENAI_API_KEY from environment

LLM_MODEL = "gpt-5.4-mini"

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"


def process_jobs():

    while True:

        db = SessionLocal()

        pending_jobs = db.query(InferenceJob).filter(
            InferenceJob.status == "pending"
        ).all()

        for job in pending_jobs:

            print(f"Processing job {job.id}")

            job.status = "running"

            db.commit()

            try:

                file_path = UPLOAD_DIR / job.filename

                print(file_path)

                # Read the file (PDF or plain text)
                if file_path.suffix.lower() == ".pdf":
                    reader = PdfReader(file_path)
                    text = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
                else:
                    with open(file_path, "r") as f:
                        text = f.read()

                # Extract title + summarize in one LLM call
                response = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are analyzing a research paper or document.

1. Extract or infer the title of this document. If it's a research paper, use the actual paper title. If no clear title exists, create a short descriptive title (max 10 words).
2. Write a clear, concise summary.

Respond in exactly this format (no extra text before or after):
TITLE: <title here>
SUMMARY: <summary here>

Document:
{text}
"""
                        }
                    ]
                )

                content = response.choices[0].message.content or ""

                # Parse TITLE / SUMMARY from response
                title = job.filename  # fallback to filename
                summary = content     # fallback to full content

                if "TITLE:" in content and "SUMMARY:" in content:
                    parts = content.split("SUMMARY:", 1)
                    title_part = parts[0].replace("TITLE:", "").strip()
                    summary_part = parts[1].strip()
                    if title_part:
                        title = title_part
                    summary = summary_part

                job.title = title
                job.summary = summary

                db.commit()

                # Chunk + embed for RAG
                store_chunks(db, job.id, text)

                job.status = "finished"

                db.commit()

                print(f"Finished job {job.id} — title: {title}")

            except Exception as e:

                print(f"Error processing job {job.id}: {e}")

                job.status = "failed"

                db.commit()

        db.close()

        time.sleep(1)


if __name__ == "__main__":

    process_jobs()
