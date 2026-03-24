from pydantic import BaseModel

class QMBallBase(BaseModel):
    striker_batsman: str | None = None
    non_striker_batsman: str | None = None
    striker_bowler: str | None = None
    non_striker_bowler: str | None = None
    current_striker_batsman: str | None = None
    current_non_striker_batsman: str | None = None
    current_striker_bowler: str | None = None
    current_non_striker_bowler: str | None = None
    is_match_start: int = 0
    run_scored: int = 0
    runs_scored: int = 0
    is_no_ball: int = 0
    is_wide_ball: int = 0
    is_bye: int = 0
    is_leg_bye: int = 0
    is_four: int = 0
    is_six: int = 0
    is_out: int = 0
    out_type: str | None = None
    over_counter: float = 0.00
    out_by: int | None = None
    is_over_completed: int = 0
    is_inning_completed: int = 0
    is_match_completed: int = 0
    team_name: str | None = None
    is_deve_record: int = 0
    out_player_name: int | None = None
    out_by_2: str | None = None
    is_first_inning: int = 0
    is_second_inning: int = 0
    inning_totals: dict | None = None
    batsman_data: dict | None = None
    bowler_data: dict | None = None

    class Config:
        from_attributes = True