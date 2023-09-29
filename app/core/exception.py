from fastapi import HTTPException


def no_such_id():
    raise HTTPException(
        status_code=404,
        detail="The user with this id does not exist in the system",
    )


def email_already_exist():
    raise HTTPException(
        status_code=404,
        detail="This email already exist"
    )


def phone_already_exist():
    raise HTTPException(
        status_code=404,
        detail="This phone already exist"
    )
