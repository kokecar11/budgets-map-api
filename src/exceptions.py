from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, message="Not Found this resource."):
        self.message = message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.message)


class BadRequestError(HTTPException):
    def __init__(
        self,
        message="Bad Request Error.",
    ):
        self.message = message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.message)


class UnauthorizedError(HTTPException):
    def __init__(self, message="User is Unauthorized"):
        self.message = message
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=self.message)


class UnauthenticatedError(HTTPException):
    def __init__(self, message="User is Unauthenticated"):
        self.message = message
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=self.message)
