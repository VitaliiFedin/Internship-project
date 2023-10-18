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


class ForbiddenToUpdateCompany(HTTPException):
    def __init__(self, detail="You can\'t update this company"):
        super().__init__(
            status_code=403,
            detail=detail,
        )


class ForbiddenToDeleteCompany(HTTPException):
    def __init__(self, detail="You can\'t delete this company"):
        super().__init__(
            status_code=403,
            detail=detail,
        )


class ForbiddenToProceed(HTTPException):
    def __init__(self, detail="You are not owner of this company"):
        super().__init__(
            status_code=403,
            detail=detail,
        )


class InvitationNotFound(HTTPException):
    def __init__(self, detail="Invitation was not found"):
        super().__init__(
            status_code=403,
            detail=detail,
        )


class RequestNotFound(HTTPException):
    def __init__(self, detail="Request was not found"):
        super().__init__(
            status_code=403,
            detail=detail,
        )
