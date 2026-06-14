from typing import Optional, Dict, Any
from .base import AppException


class BusinessLogicException(AppException):
    def __init__(self, message: str = "Ошибка бизнес-логики", status_code: int = 400, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status_code, detail=detail)


class UserNotFoundException(BusinessLogicException):
    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        if user_id:
            message = f"Пользователь с id={user_id} не найден"
            detail = {"user_id": user_id}
        elif username:
            message = f"Пользователь с username='{username}' не найден"
            detail = {"username": username}
        else:
            message = "Пользователь не найден"
            detail = {}
        super().__init__(message=message, status_code=404, detail=detail)


class PostNotFoundException(BusinessLogicException):
    def __init__(self, post_id: Optional[int] = None, slug: Optional[str] = None):
        if post_id:
            message = f"Пост с id={post_id} не найден"
            detail = {"post_id": post_id}
        elif slug:
            message = f"Пост с slug='{slug}' не найден"
            detail = {"slug": slug}
        else:
            message = "Пост не найден"
            detail = {}
        super().__init__(message=message, status_code=404, detail=detail)


class CommentNotFoundException(BusinessLogicException):
    def __init__(self, comment_id: Optional[int] = None):
        message = f"Комментарий с id={comment_id} не найден" if comment_id else "Комментарий не найден"
        detail = {"comment_id": comment_id} if comment_id else {}
        super().__init__(message=message, status_code=404, detail=detail)


class CategoryNotFoundException(BusinessLogicException):
    def __init__(self, category_id: Optional[int] = None):
        message = f"Категория с id={category_id} не найдена" if category_id else "Категория не найдена"
        detail = {"category_id": category_id} if category_id else {}
        super().__init__(message=message, status_code=404, detail=detail)


class TagNotFoundException(BusinessLogicException):
    def __init__(self, tag_id: Optional[int] = None):
        message = f"Тег с id={tag_id} не найден" if tag_id else "Тег не найден"
        detail = {"tag_id": tag_id} if tag_id else {}
        super().__init__(message=message, status_code=404, detail=detail)


class DuplicateUserException(BusinessLogicException):
    def __init__(self, field: str = "username", value: Optional[str] = None):
        message = f"Пользователь с {field}='{value}' уже существует" if value else "Пользователь уже существует"
        super().__init__(message=message, status_code=409, detail={"field": field, "value": value})


class InvalidStatusException(BusinessLogicException):
    def __init__(self, current: str, target: str):
        super().__init__(
            message=f"Нельзя изменить статус с '{current}' на '{target}'",
            status_code=422,
            detail={"current_status": current, "target_status": target}
        )