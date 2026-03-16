from pydantic import BaseModel
class CreateQuickMatchSchema(BaseModel):
    team1_name: str
    team1_image: str | None = None
    team2_name: str
    team2_image: str | None = None
    match_settings: dict | None = None
    toss_info: dict | None = None
    striker_batsman: str | None = None
    non_striker_batsman: str | None = None
    striker_bowler: str | None = None
    non_striker_bowler: str | None = None
    team_name: str | None = None