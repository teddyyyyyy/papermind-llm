# Current update:

1. User uploads txt file
        │
        ▼
2. FastAPI receives UploadFile
        │
        ▼
3. File saved into:
   app/uploads/paper.txt
        │
        ▼
4. SQLAlchemy creates DB object
        │
        ▼
5. PostgreSQL stores:
   id
   filename
   status
   created_at
        │
        ▼
6. API returns JSON response


## The output

{
  "id": 1,
  "filename": "paper.txt",
  "status": "pending",
  "created_at": "2026-05-16T16:20:00"
}
