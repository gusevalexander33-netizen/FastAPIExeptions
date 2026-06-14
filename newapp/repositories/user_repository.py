from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import User
from exeptions.infrastructure import RecordNotFoundException
from exeptions import UserNotFoundException, DuplicateUserException
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db, entity_name="Пользователь")

    def get_by_id(self, id: int) -> User:
        try:
            return super().get_by_id(id)
        except RecordNotFoundException:
            raise UserNotFoundException(user_id=id)

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            self._handle_db_error(e, "поиске пользователя по username")

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            self._handle_db_error(e, "поиске пользователя по email")

    def create(self, obj_in: dict) -> User:
        try:
            existing = self.get_by_username(obj_in.get("username"))
            if existing:
                raise DuplicateUserException(field="username", value=obj_in.get("username"))
            return super().create(obj_in)
        except DuplicateUserException:
            raise
        except Exception as e:
            self._handle_db_error(e, "создании пользователя")

    def update(self, id: int, obj_in: dict) -> User:
        try:
            if not self.exists(id):
                raise UserNotFoundException(user_id=id)
            return super().update(id, obj_in)
        except UserNotFoundException:
            raise
        except RecordNotFoundException:
            raise UserNotFoundException(user_id=id)

    def delete(self, id: int) -> User:
        try:
            if not self.exists(id):
                raise UserNotFoundException(user_id=id)
            return super().delete(id)
        except UserNotFoundException:
            raise

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return self.db.query(User) \
                .filter(User.is_active == True) \
                .offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, "получении активных пользователей")

    def get_staff_users(self) -> List[User]:
        try:
            return self.db.query(User).filter(User.is_staff == True).all()
        except Exception as e:
            self._handle_db_error(e, "получении персонала")

    def search_users(self, query: str) -> List[User]:
        try:
            search = f"%{query}%"
            return self.db.query(User).filter(
                or_(
                    User.username.like(search),
                    User.email.like(search),
                    User.first_name.like(search),
                    User.last_name.like(search)
                )
            ).all()
        except Exception as e:
            self._handle_db_error(e, "поиске пользователей")

    def get_user_posts_count(self, user_id: int) -> int:
        try:
            user = self.get_by_id(user_id)
            return len(user.posts)
        except UserNotFoundException:
            raise
        except Exception as e:
            self._handle_db_error(e, "подсчете постов пользователя")