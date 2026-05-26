from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import (
    get_categories,
    create_category,
    update_category,
    delete_category,
)

router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return get_categories(db)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_new_category(body: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, body.name, body.color or "#6366f1")


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def edit_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = update_category(db, category_id, body.name, body.color)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.delete("/categories/{category_id}", status_code=204)
def remove_category(category_id: int, db: Session = Depends(get_db)):
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
