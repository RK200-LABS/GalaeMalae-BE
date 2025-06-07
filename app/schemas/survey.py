from pydantic import BaseModel
from typing import List
class Recommendation(BaseModel):
    name: str
    score: int

class SurveySubmit(BaseModel):
    q1: str
    q2: str
    q3: str
    q4: str
    q5: str
    q6: str
    q7: str

class SurveyResult(BaseModel):
    recommendations: List[Recommendation]