from pydantic import BaseModel


class MemoryTurn(BaseModel):
    role: str
    content: str


class MemoryState(BaseModel):
    turns: list[MemoryTurn]


class CondenseRequest(BaseModel):
    followup: str


class CondenseResult(BaseModel):
    standalone_question: str
