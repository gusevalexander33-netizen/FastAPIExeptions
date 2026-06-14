from typing import Optional, Any, Dict


class AppException(Exception):
    def init(
            self,
            message: str = "Внутренняя ошибка приложения",
            status_code: int = 500,
            detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация ошибки для ответа API"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "detail": self.detail
    }