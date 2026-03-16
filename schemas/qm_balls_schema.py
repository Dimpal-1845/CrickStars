from pydantic import BaseModel

class QMBallBase(BaseModel):

    striker_batsman: str | None = None
    non_striker_batsman: str | None = None
    striker_bowler: str | None = None
    non_striker_bowler: str | None = None
   