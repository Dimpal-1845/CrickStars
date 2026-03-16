from os import utime
from fastapi import FastAPI
from pydantic import BaseModel
from db.database import engine
import db.model as models   
from datetime import date , time

app = FastAPI() 

class CreateMatchRequest(BaseModel):
    nb: bool = False
    wd: bool = False
    bye: bool = False
    lbye: bool = False
    overs: int
    no_of_bowlers: int
    powerplay_overs: int = 0
    ball_type: str = "Tennis"
    state : str | None = None
    city : str | None = None
    ground_name: str | None = None
    date: date 
    time: time 
    teams: list[dict]
    playing_eleven: list[dict]
    player_roles: list[dict]
    toss_winner_team_id: int | None = None
    chosen_to: str | None = None
#2
class TeamBase(BaseModel):
    team_id : int | None = None
    match_id : int
    team_logo : str | None = None
    deleted_at : str | None = None
    created_at : str | None = None
    updated_at : str | None = None

#1
class UserBase(BaseModel):
    user_id: int | None = None
    fname: str
    lname: str
    # accept filename or url as text; allow missing
    profile: str | None = None
    phno: int
    email: str
    gender: int = 0
    state: str = "Unknown"
    city: str | None = None
    country_code: str | None = None
    playing_role: str = "0"
    batting_role: str = "0"
    bowling_role: str = "0"
    # fields that may be null in JSON should be optional
    deleted_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    notification_token: str | None = None
    status: str = "1"
    email_verified_at: str | None = None
    remember_token: str | None = None
    token_version: int = 1


#3
'''class MatchBase(BaseModel):
    match_id: int | None = None
    match_type: int
    team1_id: int | None = None
    team2_id: int | None = None
    overs: int
    no_of_bowlers: int
    nb: bool = False
    wd: bool = False
    bye: bool = False
    lbye: bool = False
    match_is: int = 0
    state: str | None = None
    city: str | None = None
    powerplay_overs: int = 0
    ball_type: str = "Tennis"
    ground_name: str | None = None
    date: str | None = None
    time: str | None = None
    deleted_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    winning_team: str | None = None
    win_by: str | None = None '''

#4
class PlayerBase(BaseModel):
    players_id: int | None = None
    team_id: int | None = None
    name: str
    batting_style: str
    bowling_style: str

#5
class QuickMatchBase(BaseModel):
    match_status: int = 0
    team1_name: str
    team1_image: str | None = None
    team2_name: str
    team2_image: str | None = None
    match_settings: dict | None = None
    toss_info: dict | None = None
    winning_team: str | None = None
    win_by: str | None = None
    match_transfer_user_id: int
    player_id: int

#6
class BattingBase(BaseModel):
    id: int | None = None
    batting_style_name: str
    created_at: str | None = None
    updated_at: str | None = None

#7
class BowlingBase(BaseModel):
    id: int | None = None
    bowling_style_name: str

#8
class BallBase(BaseModel):
    ball_id: int | None = None
    match_id: int
    striker_batsman_id: int
    nonstriker_batsman_id: int
    striker_bowler_id: int
    nonstriker_bowler_id: int
    current_striker_batsman: int
    current_non_striker_batsman: int
    current_striker_bowler: int
    current_non_striker_bowler: int
    is_match_start: bool = False
    runs_scored: int = 0
    is_no_ball: bool = False
    is_wide_ball: bool = False
    is_bye: bool = False
    is_leg_bye: bool = False
    is_four: bool = False
    is_six: bool = False
    is_out: bool = False
    out_type: str | None = None
    over_counter: float = 0.00
    out_by: int | None = None
    is_over_completed: bool = False
    is_inning_completed: bool = False
    is_match_completed: bool = False
    team_id: int
    is_deve_record: bool = False
    out_player_id: int | None = None
    is_first_inning: bool = False
    is_second_inning: bool = False
    out_by_2: int | None = None
    inning_totals: dict
    batsman_data: dict
    bowler_data: dict
#9
class TeamPlayersSearchBase(BaseModel):
    id: int | None = None
    user_id: int
    team_name: str
    player_name: str

#10
class StateBase(BaseModel):
    state_id: int | None = None
    state_name: str

#11
class PlayingRoleBase(BaseModel):
    id: int | None = None
    playing_role_name: str
#12  
class AppVersionBase(BaseModel):
    id: int | None = None
    device_name: str
    version: str
    must_update: int = 0
    base_url: str
    active_version: str
#13
class PlayerRoleBase(BaseModel):
    id: int | None = None
    match_id: int
    team_id: int | None = None
    captain_player_id: int | None = None
    wicketkeeper_player_id: int | None = None
#14
class PlayingElevenBase(BaseModel):
    id: int | None = None
    match_id: int
    team_id: int
    player_id: int

#15
class QMBallBase(BaseModel):
    ball_id: int | None = None
    match_id: int | None = None
    striker_batsman: str | None = None
    nonstriker_batsman: str | None = None
    striker_bowler: str | None = None
    nonstriker_bowler: str | None = None
    current_striker_batsman: str | None = None
    current_non_striker_batsman: str | None = None
    current_striker_bowler: str | None = None
    current_non_striker_bowler: str | None = None
    runs_scored: int = 0
    team_name: str | None = None
    inning_totals: dict | None = None
    batsman_data: dict | None = None
    bowler_data: dict | None = None

#16
class ShareTeamBase(BaseModel):
    id: int | None = None
    owner_id: int
    share_with_id: int
    team_id: int
    new_team_id: int

#17
class CityBase(BaseModel):
    id: int | None = None
    state_id: int
    city_name: str


#18
class InningBase(BaseModel):
    inning_id: int | None = None
    match_id: int
    first_inning_id: int
    second_inning_id: int


#19
class TossBase(BaseModel):
    toss_id: int | None = None
    match_id: int
    toss_winner_team_id: int
    chosen_to: str

#20
class TeamMasterBase(BaseModel):
    team_id: int | None = None
    team_name: str
    state: str
    city: str
    team_image: str
    status: int = 1

#21  
class TeamPlayersBase(BaseModel):
    team_player_id: int | None = None
    team_id: int
    player_id: int
    first_name: str | None = None
    last_name: str | None = None
    is_captain: int = 0
    is_wicketkeeper: int = 0
