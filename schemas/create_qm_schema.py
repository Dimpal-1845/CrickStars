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


class UpdateQuickMatchSchema(BaseModel):
    team1_name: str | None = None
    team1_image: str | None = None
    team2_name: str | None = None
    team2_image: str | None = None
    match_settings: dict | None = None
    toss_info: dict | None = None
    winning_team: str | None = None
    win_by: str | None = None
    match_status: int | None = None