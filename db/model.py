from os import utime
from sqlite3 import Date
from sqlalchemy import Boolean, Column, Integer, String, LargeBinary, Float, DateTime, BigInteger, SmallInteger, JSON, Table, func, ForeignKey 
from db.database import Base 
from datetime import datetime

teams = {}

class Matches(Base):
    __tablename__ = 'matches'

    match_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nb = Column(Boolean, nullable=False, default=False)   # No Ball allowed
    wd = Column(Boolean, nullable=False, default=False)   # Wide Ball allowed
    bye = Column(Boolean, nullable=False, default=False)
    lbye = Column(Boolean, nullable=False, default=False)
    overs = Column(Integer, nullable=False)
    no_of_bowlers = Column(Integer, nullable=False)
    powerplay_overs = Column(Integer, default=0)
    ball_type = Column(String(255), nullable=False, default='Tennis')
    state = Column(String(255), default=None)
    city = Column(String(255), default=None)
    ground_name = Column(String(255), default=None)
    date = Column(DateTime, default=Date)
    time = Column(DateTime, default=utime)
    teams = Column(JSON, nullable=False)
    playing_eleven = Column(JSON, nullable=False)
    player_roles = Column(JSON, nullable=False)
    toss_winner_team_id = Column(BigInteger, default=None)
    chosen_to = Column(String(255), default=None)
    match_is = Column(SmallInteger, nullable=False, default=0)  # 0 - ongoing, 1 - complete
    deleted_at = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    fname = Column(String(255), default=None)
    lname = Column(String(255), default=None)
    # store profile filename/URL as text (was LargeBinary which expects bytes)
    profile = Column(String(255), default=None)
    # phone numbers can be larger than 32-bit int; use BigInteger
    phno = Column(BigInteger, unique=True, nullable=False)
    email = Column(String(255), default=None)
    gender = Column(SmallInteger, nullable=False, default=0)  # 0 - Male, 1 - Female
    state = Column(String(255), nullable=False, default='Unknown')
    city = Column(String(255), default=None)
    country_code = Column(String(10), default=None)
    playing_role = Column(String(255), nullable=False, default='0')
    batting_role = Column(String(255), nullable=False, default='0')
    bowling_role = Column(String(255), nullable=False, default='0')
    deleted_at = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notification_token = Column(String(255), default=None)
    status = Column(String(255), nullable=False, default='1')
    email_verified_at = Column(DateTime, default=None)
    remember_token = Column(String(255), default=None)
    token_version = Column(BigInteger, nullable=False, default=1)

class QuickMatch(Base):
    __tablename__ = 'qm_match'

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    match_status = Column(Integer, nullable=False, default=0)
    team1_name = Column(String(255), nullable=False)
    team1_image = Column(String(255), default=None)
    team2_name = Column(String(255), nullable=False)
    team2_image = Column(String(255), default=None)
    match_settings = Column(JSON, default=None)
    toss_info = Column(JSON, default=None)
    winning_team = Column(String(255), default=None)
    win_by = Column(String(255), default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,onupdate=datetime.utcnow)
    match_transfer_user_id = Column(BigInteger, nullable=False , default=0)  # 0 means not transferred; otherwise store user_id of new owner
    player_id = Column(BigInteger, nullable=False , default=0)  # store player_id of the user who created the match for ownership tracking

class Ball(Base):
    __tablename__ = "balls"

    ball_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(BigInteger, nullable=False)
    striker_batsman_id = Column(BigInteger, nullable=False)
    non_striker_batsman_id = Column(BigInteger, nullable=False)
    striker_bowler_id = Column(BigInteger, nullable=False)
    non_striker_bowler_id = Column(BigInteger, nullable=False)
    current_striker_batsman = Column(BigInteger, nullable=False)
    current_non_striker_batsman = Column(BigInteger, nullable=False)
    current_striker_bowler = Column(BigInteger, nullable=False)
    current_non_striker_bowler = Column(BigInteger, nullable=False)
    is_match_start = Column(Boolean, default=False)
    runs_scored = Column(Integer, default=0)
    is_no_ball = Column(Boolean, default=False)
    is_wide_ball = Column(Boolean, default=False)
    is_bye = Column(Boolean, default=False)
    is_leg_bye = Column(Boolean, default=False)
    is_four = Column(Boolean, default=False)
    is_six = Column(Boolean, default=False)
    is_out = Column(Boolean, default=False)
    out_type = Column(String(255), nullable=True)
    over_counter = Column(Float, default=0.00)
    out_by = Column(BigInteger, nullable=True)
    is_over_completed = Column(Boolean, default=False)
    is_inning_completed = Column(Boolean, default=False)
    is_match_completed = Column(Boolean, default=False)
    team_id = Column(BigInteger, nullable=False)
    is_deve_record = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    out_player_id = Column(BigInteger, nullable=True)
    is_first_inning = Column(Boolean, default=False)
    is_second_inning = Column(Boolean, default=False)
    out_by_2 = Column(BigInteger, nullable=True)
    # optional JSON summaries; default to empty dict to avoid insert-time errors
    inning_totals = Column(JSON, nullable=True, default=dict)
    batsman_data = Column(JSON, nullable=True, default=dict)
    bowler_data = Column(JSON, nullable=True, default=dict)
 

class Teams(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    # store logo as a URL/path string instead of raw binary for simplicity; 
    team_logo = Column(String(255), default=None)
    deleted_at = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Players(Base):
    __tablename__ = 'players'

    players_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=True)
    name = Column(String(255), nullable=False)
    batting_style = Column(String(255), nullable=True)
    bowling_style = Column(String(255), nullable=True)


class Batting(Base):
    __tablename__ = 'batting'

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    batting_style_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Bowling(Base):
    __tablename__ = 'bowling'

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    bowling_style_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer , primary_key=True, index=True, nullable=False, autoincrement=True)
    state_id =  Column(Integer , ForeignKey("states.state_id") , nullable=False)
    city_name = Column(String(255) , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class States(Base):
    __tablename__ = 'states'

    state_id = Column(Integer , primary_key=True, index=True, nullable=False, autoincrement=True)
    state_name = Column(String(255) , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Innings(Base):
    __tablename__ = 'innings'

    inning_id = Column(Integer , primary_key=True, index=True, nullable=False, autoincrement=True)
    match_id = Column(BigInteger, ForeignKey("matches.match_id"), nullable=False)
    first_inning_id = Column(BigInteger , nullable=False) 
    second_inning_id = Column(BigInteger , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Toss(Base):
    __tablename__ = 'toss'
    toss_id = Column(Integer , primary_key=True, index=True, nullable=False, autoincrement=True)
    match_id = Column(BigInteger, ForeignKey("matches.match_id"), nullable=False)
    toss_winner_team_id = Column(BigInteger, nullable=False)
    chosen_to = Column(String(255) , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class app_version_updates(Base) :
    __tablename__ = 'app_version_updates'

    id = Column(BigInteger , primary_key=True, index=True, nullable=False, autoincrement=True)
    device_name = Column(String(255) , nullable=False)
    version = Column(String(255) , nullable=False)
    must_update = Column(SmallInteger , nullable=False , default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    base_url = Column(String(255) , nullable=False)
    active_version = Column(String(255) , nullable=False)

class Player_roles(Base):
    __tablename__ = 'player_roles'

    id = Column(BigInteger , primary_key=True, index=True, nullable=False, autoincrement=True)
    match_id = Column(BigInteger, ForeignKey("matches.match_id"), nullable=False)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=True)
    captain_player_id = Column(BigInteger , nullable=True)
    wicketkeeper_player_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Playing_elevens(Base):
    __tablename__ = 'playing_elevens'

    id = Column(BigInteger , primary_key=True, index=True, nullable=False, autoincrement=True)
    match_id = Column(BigInteger, ForeignKey("matches.match_id"), nullable=False)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=True)
    player_id = Column(BigInteger, ForeignKey("players.players_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Playing_roles(Base): 
    __tablename__ = 'playing_roles'

    id = Column(BigInteger , primary_key=True, index=True, nullable=False, autoincrement=True)
    playing_role_name = Column(String(255) , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QMBall(Base):
    __tablename__ = "qm_balls"

    ball_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(BigInteger, nullable=False)
    striker_batsman = Column(String(255), nullable=False)
    non_striker_batsman = Column(String(255), nullable=False)
    striker_bowler = Column(String(255), nullable=False)
    non_striker_bowler = Column(String(255), nullable=False)
    current_striker_batsman = Column(String(255), nullable=False)
    current_non_striker_batsman = Column(String(255), nullable=False)
    current_striker_bowler = Column(String(255), nullable=False)
    current_non_striker_bowler = Column(String(255), nullable=False)
    is_match_start = Column(Boolean, default=False)
    run_scored = Column(Integer, default=0)
    is_no_ball = Column(Boolean, default=False)
    is_wide_ball = Column(Boolean, default=False)
    is_bye = Column(Boolean, default=False)
    is_leg_bye = Column(Boolean, default=False)
    is_four = Column(Boolean, default=False)
    is_six = Column(Boolean, default=False)
    is_out = Column(Boolean, default=False)
    out_type = Column(String(255), nullable=True)
    over_counter = Column(Float, default=0.00)
    out_by = Column(BigInteger, nullable=True)
    is_over_completed = Column(Boolean, default=False)
    is_inning_completed = Column(Boolean, default=False)
    is_match_completed = Column(Boolean, default=False)
    team_name = Column(String(255), nullable=False)
    is_deve_record = Column(Boolean, default=False)
    out_player_name = Column(BigInteger, nullable=True , default=None)
    out_by_2 = Column(String(255), nullable=True , default=None)
    is_first_inning = Column(Boolean, default=False)
    is_second_inning = Column(Boolean, default=False)
    inning_totals = Column(JSON, nullable=True, default=dict)
    batsman_data = Column(JSON, nullable=True, default=dict)
    bowler_data = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Share_team(Base):
    __tablename__ = 'share_team'
     
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    owner_id = Column(Integer , nullable=False)
    share_with_id = Column(BigInteger , nullable=False)
    team_id = Column(BigInteger , nullable=False)
    new_team_id = Column(BigInteger , nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class TeamMaster(Base):
    __tablename__ = 'team_masters'

    team_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    team_name = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    team_image = Column(String(255), nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)
    created_by = Column(BigInteger, nullable=False)
    updated_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class TeamPlayers(Base):
    __tablename__ = 'team_players'

    team_player_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    team_id = Column(BigInteger, nullable=False)
    player_id = Column(BigInteger, nullable=False)
    first_name = Column(String(255), default=None)
    last_name = Column(String(255), default=None)
    is_captain = Column(SmallInteger, nullable=False, default=0)
    is_wicketkeeper = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class TeamPlayersSearch(Base):
    __tablename__ = 'team_players_search'

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    team_name = Column(String(255), nullable=False)
    player_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)