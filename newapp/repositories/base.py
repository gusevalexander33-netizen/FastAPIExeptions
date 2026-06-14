from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database import Base
from exeptions import DatabaseException, RecordNotFoundException, UniqueConstraintException

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session, entity_name: str = "Запись"):
        self.model = model
        self.db = db
        self.entity_name = entity_name

    def _handle_db_error(self, error: Exception, operation: str = "операции"):
        if isinstance(error, IntegrityError):
            raise UniqueConstraintException(entity=self.entity_name)
        elif isinstance(error, SQLAlchemyError):
            raise DatabaseException(
                message=f"Ошибка БД при {operation}",
                original_error=error
            )
        raise DatabaseException(message=f"Неизвестная ошибка при {operation}")

    def get_by_id(self, id: int) -> ModelType:
        try:
            db_obj = self.db.query(self.model).filter(self.model.id == id).first()
            if db_obj is None:
                raise RecordNotFoundException(entity=self.entity_name, entity_id=id)
            return db_obj
        except AppException:
            raise
        except Exception as e:
            self._handle_db_error(e, f"получении {self.entity_name}")

    def get_by_id_or_none(self, id: int) -> Optional[ModelType]:
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            self._handle_db_error(e, f"получении {self.entity_name}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            self._handle_db_error(e, f"получении списка {self.entity_name}")

    def create(self, obj_in: dict) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            self.db.rollback()
            raise UniqueConstraintException(entity=self.entity_name)
        except Exception as e:
            self.db.rollback()
            self._handle_db_error(e, f"создании {self.entity_name}")

    def update(self, id: int, obj_in: dict) -> ModelType:
        try:
            db_obj = self.get_by_id(id)
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except AppException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            self._handle_db_error(e, f"обновлении {self.entity_name}")

    def delete(self, id: int) -> ModelType:
        try:
            db_obj = self.get_by_id(id)
            self.db.delete(db_obj)
            self.db.commit()
            return db_obj
        except AppException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            self._handle_db_error(e, f"удалении {self.entity_name}")

    def count(self) -> int:
        try:
            return self.db.query(self.model).count()
        except Exception as e:
            self._handle_db_error(e, f"подсчете {self.entity_name}")

    def exists(self, id: int) -> bool:
        try:
            return self.db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            self._handle_db_error(e, f"проверке {self.entity_name}")

from exeptions import AppException