from fastapi import HTTPException


class MyNotFoundException(HTTPException):
    def __init__(self, detail="Resource not found"):
        super().__init__(
            status_code=404,
            detail=detail,
        )


def no_such_id():
    raise MyNotFoundException(
        detail="The user with this id does not exist in the system"
    )


def email_already_exist():
    raise MyNotFoundException(
        detail="This email already exist"
    )


def phone_already_exist():
    raise MyNotFoundException(
        detail="This phone already exist"
    )
