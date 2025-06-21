from pydantic import BaseModel


class PlanRequest(BaseModel):
    destination: str
    schedule: str