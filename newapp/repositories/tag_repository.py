from typing import Optional
from sqlalchemy.orm import Session
from models import Tag
from exeptions.infrastructure import RecordNotFoundException
from exeptions.domain import TagNotFoundException
from .base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: Session):
        super().__init__(Tag, db, entity_name="Тег")

    def get_by_id(self, id: int) -> Tag:
        try:
            return super().get_by_id(id)
        except RecordNotFoundException:
            raise TagNotFoundException(tag_id=id)

    def get_by_slug(self, slug: str) -> Optional[Tag]:
        try:
            return self.db.query(Tag).filter(Tag.slug == slug).first()
        except Exception as e:
            self._handle_db_error(e, "поиске тега по slug")

    def get_or_create(self, name: str, slug: str) -> Tag:
        tag = self.get_by_slug(slug)
        if not tag:
            tag = self.create({"name": name, "slug": slug})
        return tag