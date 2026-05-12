from fastapi import Response
class JSONResponse(Response):
    def __init__(self, status_code=200, content=None):
        super().__init__(status_code=status_code, content=content)
