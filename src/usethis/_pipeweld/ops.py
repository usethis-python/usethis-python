from pydantic import BaseModel


class BaseOperation(BaseModel):
    after: str | None  # None represents the source node
    step: str


class InsertParallel(BaseOperation):
    pass


class InsertSuccessor(BaseOperation):
    pass


type Instruction = InsertSuccessor | InsertParallel
