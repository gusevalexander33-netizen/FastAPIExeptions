from typing import Optional, Any, Dict
from .base import AppException


class DatabaseException(AppException):
    def __init__(
        self,
        message: str = "Ошибка базы данных",
        detail: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message=message, status_code=500, detail=detail)
        self.original_error = original_error


class RecordNotFoundException(DatabaseException):
    def __init__(self, entity: str = "Запись", entity_id: Optional[int] = None):
        message = f"{entity} с id={entity_id} не найден(а)" if entity_id else f"{entity} не найден(а)"
        super().__init__(
            message=message,
            status_code=404,
            detail={"entity": entity, "entity_id": entity_id}
        )


class UniqueConstraintException(DatabaseException):
    def __init__(self, entity: str = "Запись", field: str = "поле", value: Optional[Any] = None):
        message = f"{entity} с таким {field} уже существует"
        if value:
            message += f": '{value}'"
        super().__init__(
            message=message,
            status_code=409,
            detail={"entity": entity, "field": field, "value": value}
        )


class ConnectionException(DatabaseException):
    def __init__(self, original_error: Optional[Exception] = None):
        super().__init__(
            message="Не удалось подключиться к базе данных",
            status_code=503,
            original_error=original_error
        )