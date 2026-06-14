from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from models import Post
from exeptions.infrastructure import RecordNotFoundException
from exeptions.domain import PostNotFoundException, InvalidStatusException
from .base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, db: Session):
        super().__init__(Post, db, entity_name="Пост")

    def get_by_id(self, id: int) -> Post:
        try:
            return super().get_by_id(id)
        except RecordNotFoundException:
            raise PostNotFoundException(post_id=id)

    def get_by_slug(self, slug: str) -> Optional[Post]:
        try:
            return self.db.query(Post).filter(Post.slug == slug).first()
        except Exception as e:
            self._handle_db_error(e, "поиске поста по slug")

    def get_published_posts(self, skip: int = 0, limit: int = 100) -> List[Post]:
        try:
            return self.db.query(Post) \
                .filter(Post.status == "published") \
                .order_by(Post.published_at.desc()) \
                .offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, "получении опубликованных постов")

    def get_draft_posts(self, skip: int = 0, limit: int = 100) -> List[Post]:
        try:
            return self.db.query(Post) \
                .filter(Post.status == "draft") \
                .offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, "получении черновиков")

    def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        try:
            return self.db.query(Post) \
                .filter(Post.author_id == user_id) \
                .offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, f"получении постов пользователя {user_id}")

    def get_category_posts(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        try:
            return self.db.query(Post) \
                .filter(Post.category_id == category_id) \
                .offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, f"получении постов категории {category_id}")

    def update(self, id: int, obj_in: dict) -> Post:
        try:
            if not self.exists(id):
                raise PostNotFoundException(post_id=id)
            if "status" in obj_in:
                current = self.get_by_id(id)
                if not self._valid_transition(current.status, obj_in["status"]):
                    raise InvalidStatusException(current.status, obj_in["status"])
            return super().update(id, obj_in)
        except (PostNotFoundException, InvalidStatusException):
            raise

    def delete(self, id: int) -> Post:
        try:
            if not self.exists(id):
                raise PostNotFoundException(post_id=id)
            return super().delete(id)
        except PostNotFoundException:
            raise

    def search_posts(self, query: str) -> List[Post]:
        try:
            search = f"%{query}%"
            return self.db.query(Post).filter(
                Post.title.like(search) | Post.content.like(search)
            ).all()
        except Exception as e:
            self._handle_db_error(e, "поиске постов")

    def publish_post(self, post_id: int) -> Post:
        try:
            post = self.get_by_id(post_id)
            if post.status not in ["draft"]:
                raise InvalidStatusException(post.status, "published")
            return self.update(post_id, {
                "status": "published","published_at": datetime.now()
            })
        except (PostNotFoundException, InvalidStatusException):
            raise

    def increment_views(self, post_id: int) -> Post:
        try:
            post = self.get_by_id(post_id)
            post.views_count += 1
            self.db.commit()
            self.db.refresh(post)
            return post
        except PostNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            self._handle_db_error(e, "увеличении просмотров")

    def _valid_transition(self, current: str, target: str) -> bool:
        transitions = {
            "draft": ["published"],
            "published": ["archived"],
            "archived": ["draft"]
        }
        return target in transitions.get(current, [])