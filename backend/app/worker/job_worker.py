import time

from pathlib import Path

from app.config.database import SessionLocal

from app.models.inference_job import InferenceJob

import ollama

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

            file_path = UPLOAD_DIR / job.filename

            print(file_path)

            with open(file_path, "r") as f:

                text = f.read()

            response = ollama.chat(
                model="qwen2.5:3b",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Summarize the following document clearly and concisely.

                        Document:
                        {text}
                        """
                    }
                ]
            )

            summary = response["message"]["content"]

            job.summary = summary

            job.status = "finished"

            db.commit()

            print(f"Finished job {job.id}")

        db.close()

        time.sleep(1)


if __name__ == "__main__":

    process_jobs()
