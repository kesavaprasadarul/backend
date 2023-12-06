from fastapi import HTTPException


class ObjectNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Object not found")
