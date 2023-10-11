from fastapi import HTTPException


class MyNotFoundException(HTTPException):
    def __init__(self, detail="Resource not found"):
        super().__init__(
            status_code=404,
            detail=detail,
        )


class NoSuchId(HTTPException):
    def __init__(self, detail="No such id exist in the system"):
        super().__init__(
            status_code=404,
            detail=detail,
        )


class EmailExist(HTTPException):
    def __init__(self, detail="This email already exist"):
        super().__init__(
            status_code=404,
            detail=detail,
        )


class PhoneExist(HTTPException):
    def __init__(self, detail="This phone already exist"):
        super().__init__(
            status_code=404,
            detail=detail,
        )


class ForbiddenToUpdate(HTTPException):
    def __init__(self, detail="You can\'t update this user"):
        super().__init__(
            status_code=403,
            detail=detail,
        )


class ForbiddenToDelete(HTTPException):
    def __init__(self, detail="You can\'t delete this user"):
        super().__init__(
            status_code=403,
            detail=detail,
        )
