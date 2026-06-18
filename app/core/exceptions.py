class AppException(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(AppException):
    def __init__(self, resource_name: str, resource_id: int) -> None:
        super().__init__(
            error="RESOURCE_NOT_FOUND",
            message=f"{resource_name} nao encontrado.",
            status_code=404,
            details={"id": resource_id},
        )
