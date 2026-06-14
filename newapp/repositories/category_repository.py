from typing import Optional, List
from sqlalchemy.orm import Session
from models import Category
from exeptions.infrastructure import RecordNotFoundException
from exeptions.domain import CategoryNotFoundException
from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db, entity_name="Категория")

    def get_by_id(self, id: int) -> Category:
        try:
            return super().get_by_id(id)
        except RecordNotFoundException:
            raise CategoryNotFoundException(category_id=id)

    def get_by_slug(self, slug: str) -> Optional[Category]:
        try:
            return self.db.query(Category).filter(Category.slug == slug).first()
        except Exception as e:
            self._handle_db_error(e, "поиске категории по slug")