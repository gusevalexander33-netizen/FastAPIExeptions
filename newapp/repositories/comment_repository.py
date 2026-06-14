from typing import List
from sqlalchemy.orm import Session
from models import Comment
from exeptions.infrastructure import RecordNotFoundException
from exeptions.domain import CommentNotFoundException
from .base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def init(self, db: Session):
        super().init(Comment, db, entity_name="Комментарий")

    def get_by_id(self, id: int) -> Comment:
        try:
            return super().get_by_id(id)
        except RecordNotFoundException:
            raise CommentNotFoundException(comment_id=id)

    def delete(self, id: int) -> Comment:
        try:
            if not self.exists(id):
                raise CommentNotFoundException(comment_id=id)
            return super().delete(id)
        except CommentNotFoundException:
            raise

    def get_post_comments(self, post_id: int) -> List[Comment]:
        try:
            return self.db.query(Comment) \
                .filter(Comment.post_id == post_id, Comment.parent_id == None) \
                .order_by(Comment.created_at.desc()).all()
        except Exception as e:
            self._handle_db_error(e, f"получении комментариев поста")

    def get_user_comments(self, user_id: int) -> List[Comment]:
        try:
            return self.db.query(Comment) \
                .filter(Comment.author_id == user_id) \
                .order_by(Comment.created_at.desc()).all()
        except Exception as e:
            self._handle_db_error(e, f"получении комментариев пользователя")