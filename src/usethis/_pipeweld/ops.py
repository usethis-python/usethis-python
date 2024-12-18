from pydantic import BaseModel


class BaseOperation(BaseModel):
    before: str | None  # None represents the source node
    step: str


class InsertParallel(BaseOperation):
    pass
