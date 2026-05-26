from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.inference_job import InferenceJob


def get_categories(db: Session):
    return db.query(Category).order_by(Category.created_at).all()


def create_category(db: Session, name: str, color: str = "#6366f1") -> Category:
    cat = Category(name=name, color=color)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category_id: int, name: str | None, color: str | None) -> Category | None:
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return None
    if name is not None:
        cat.name = name
    if color is not None:
        cat.color = color
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, category_id: int) -> bool:
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return False
    # Unassign jobs in this category
    db.query(InferenceJob).filter(
        InferenceJob.category_id == category_id
    ).update({"category_id": None})
    db.delete(cat)
    db.commit()
    return True
