import time

from pathlib import Path

from app.config.database import SessionLocal

from app.models.inference_job import InferenceJob

from app.services.rag_service import store_chunks

import ollama

from pypdf import PdfReader


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

                # Step 1: Summarize the full document
                response = ollama.chat(
                    model="qwen2.5:3b",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Summarize the following document clearly and concisely.

Document:
{text}
"""
                        }
                    ]
                )

                summary = response["message"]["content"]

                job.summary = summary

                db.commit()

                # Step 2: Chunk + embed for RAG
                store_chunks(db, job.id, text)

                job.status = "finished"

                db.commit()

                print(f"Finished job {job.id}")

            except Exception as e:

                print(f"Error processing job {job.id}: {e}")

                job.status = "failed"

                db.commit()

        db.close()

        time.sleep(1)


if __name__ == "__main__":

    process_jobs()
