from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import create_match_route

app = FastAPI(
    title="CrickStars",
    description="Cricket match management system",
    version="1.0.0",
    debug=True
)

# Routers
app.include_router(create_match_route.router)
app.include_router(create_match_route.legacy_router)

# Static files (css/js/images)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]  
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard - All matches view"""
    return templates.TemplateResponse("all_matches.html", {"request": request})

@app.get("/match/{match_id}", response_class=HTMLResponse)
async def match_detail(request: Request, match_id: int):
    """Match detail page"""
    return templates.TemplateResponse("index.html", {"request": request, "match_id": match_id})

@app.get("/live", response_class=HTMLResponse)
async def live_view(request: Request):
    """Live match view"""
    return templates.TemplateResponse("live.html", {"request": request})

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CrickStars API"}
'''
@app.post("/matches/", status_code=status.HTTP_201_CREATED)
async def create_match(match: CreateMatchRequest, db: db_dependency):
    match_data = match.dict(exclude_none=True)
    db_match = models.Matches(**match_data)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

app.post("/balls/", status_code=status.HTTP_201_CREATED)
async def create_ball(ball: BallBase, db: db_dependency):
    ball_data = ball.dict(exclude_none=True)
    db_ball = models.Ball(**ball_data)
    db.add(db_ball)
    db.commit()
    db.refresh(db_ball)
    return db_ball


@app.get("/balls/{ball_id}" , status_code=status.HTTP_200_OK)
def get_ball(ball_id: int, db: Session = Depends(get_db)):
    ball = db.query(models.Ball).filter(models.Ball.ball_id == ball_id).first()
    if not ball:
        raise HTTPException(status_code=404, detail="Ball not found")
    return ball


@app.get("/balls/" , status_code=status.HTTP_200_OK)
def get_all_balls(db: Session = Depends(get_db)):
    return db.query(models.Ball).all()


@app.put("/balls/{ball_id}" , status_code=status.HTTP_200_OK)
def update_ball(ball_id: int, updated_ball: BallBase, db: Session = Depends(get_db)):
    ball = db.query(models.Ball).filter(models.Ball.ball_id == ball_id).first()
    if not ball:
        raise HTTPException(status_code=404, detail="Ball not found")
    update_data = updated_ball.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ball, key, value)
    db.commit()
    db.refresh(ball)
    return ball


@app.delete("/balls/{ball_id}" , status_code=status.HTTP_200_OK)
def delete_ball(ball_id: int, db: Session = Depends(get_db)):
    ball = db.query(models.Ball).filter(models.Ball.ball_id == ball_id).first()
    if not ball:
        raise HTTPException(status_code=404, detail="Ball not found")
    db.delete(ball)
    db.commit()
    return {"message": f"Ball record {ball_id} deleted successfully"}

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    user_data = user.dict(exclude_none=True)
    db_user = models.Users(**user_data)
    db.add(db_user)
    db.commit() 
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/" , status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@app.put("/users/{user_id}" , status_code=status.HTTP_200_OK)
def update_user(user_id: int, updated_user : UserBase, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = updated_user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}" , status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User record {user_id} deleted successfully"}

@app.post("/players/", status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerBase, db: db_dependency):
    player_data = player.dict(exclude_none=True)
    db_player = models.Players(**player_data)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@app.get("/players/{player_id}", status_code=status.HTTP_200_OK)
async def get_player(player_id: int, db: db_dependency):
    player = db.query(models.Players).filter(models.Players.players_id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/players/" , status_code=status.HTTP_200_OK)
def get_all_players(db: Session = Depends(get_db)):
    return db.query(models.Players).all()


@app.put("/players/{player_id}" , status_code=status.HTTP_200_OK)
def update_player(player_id: int, updated_player: PlayerBase, db: Session = Depends(get_db)):
    player = db.query(models.Players).filter(models.Players.players_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    update_data = updated_player.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(player, key, value)
    db.commit()
    db.refresh (player)
    return player


@app.delete("/players/{player_id}" , status_code=status.HTTP_200_OK)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Players).filter(models.Players.players_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    db.commit()
    return {"message": f"Player record {player_id} deleted successfully"}

@app.post("/matches/", status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchBase, db: db_dependency):
    match_data = match.dict(exclude_none=True)
    db_match = models.Matches(**match_data)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.get("/matches/{match_id}", status_code=status.HTTP_200_OK)
async def read_match(match_id: int, db: db_dependency):
    match = db.query(models.Matches).filter(models.Matches.match_id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.get("/matchs/" , status_code=status.HTTP_200_OK)
def get_all_matchs(db: Session = Depends(get_db)):
    return db.query(models.Matches).all()


@app.put("/matchs/{match_id}" , status_code=status.HTTP_200_OK)
def update_match(match_id: int, updated_match: MatchBase, db: Session = Depends(get_db)):
    match = db.query(models.Matches).filter(models.Matches.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    update_data = updated_match.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(match, key, value)
    db.commit()
    db.refresh(match)
    return match


@app.delete("/matchs/{match_id}" , status_code=status.HTTP_200_OK)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Matches).filter(models.Matches.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
    return {"message": f"Match record {match_id} deleted successfully"}


@app.post("/teams/", status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamBase, db: db_dependency):
    team_data = team.dict(exclude_none=True)
    db_team = models.Teams(**team_data)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/teams/{team_id}", status_code=status.HTTP_200_OK)
async def read_team(team_id: int, db: db_dependency):
    db_team = db.query(models.Teams).filter(models.Teams.team_id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@app.get("/teams/" , status_code=status.HTTP_200_OK)
def get_all_teams(db: Session = Depends(get_db)):
    return db.query(models.Teams).all()


@app.put("/teams/{team_id}" , status_code=status.HTTP_200_OK)
def update_team(team_id: int, update_team: TeamBase, db: Session = Depends(get_db)):
    db_team = db.query(models.Teams).filter(models.Teams.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = update_team.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_team, key, value)
    db.commit()
    db.refresh(db_team)
    return db_team


@app.delete("/teams/{team_id}" , status_code=status.HTTP_200_OK)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(models.Teams).filter(models.Teams.team_id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(db_team)
    db.commit()
    return {"message": f"Teams record {team_id} deleted successfully"}

@app.post("/batting/", status_code=status.HTTP_201_CREATED)
async def create_batting_style(batting: BattingBase, db: db_dependency):
    batting_data = batting.dict(exclude_none=True)
    db_batting = models.Batting(**batting_data)
    db.add(db_batting)
    db.commit()
    db.refresh(db_batting)
    return db_batting


@app.post("/bowling/", status_code=status.HTTP_201_CREATED)
async def create_bowling_style(bowling: BowlingBase, db: db_dependency):
    bowling_data = bowling.dict(exclude_none=True)
    db_bowling = models.Bowling(**bowling_data)
    db.add(db_bowling)
    db.commit()
    db.refresh(db_bowling)
    return db_bowling

@app.post("/states/", status_code=status.HTTP_201_CREATED)
async def create_state(state: StateBase, db: db_dependency):
    state_data = state.dict(exclude_none=True)
    db_state = models.States(**state_data)
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

@app.get("/states/{state_id}")
async def get_state(state_id: int, db: db_dependency):
    state = db.query(models.States).filter(models.States.state_id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state

@app.get("/states/")
async def get_all_states(db: db_dependency):
    return db.query(models.States).all()

@app.put("/states/{state_id}")
async def update_state(state_id: int, updated_state: StateBase, db: db_dependency):
    state = db.query(models.States).filter(models.States.state_id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    update_data = updated_state.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(state, key, value)
    db.commit()
    db.refresh(state)
    return state

@app.delete("/states/{state_id}")
async def delete_state(state_id: int, db: db_dependency):
    state = db.query(models.States).filter(models.States.state_id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    db.delete(state)
    db.commit()
    return {"message": f"State {state_id} deleted successfully"}

@app.post("/cities/", status_code=status.HTTP_201_CREATED)
async def create_city(city: CityBase, db: db_dependency):
    city_data = city.dict(exclude_none=True)
    db_city = models.Cities(**city_data)
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@app.get("/cities/{id}")
async def get_city(id: int, db: db_dependency):
    city = db.query(models.Cities).filter(models.Cities.id == id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@app.get("/cities/")
async def get_all_cities(db: db_dependency):
    return db.query(models.Cities).all()

@app.put("/cities/{id}")
async def update_city(id: int, updated_city: CityBase, db: db_dependency):
    city = db.query(models.Cities).filter(models.Cities.id == id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    update_data = updated_city.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(city, key, value)
    db.commit()
    db.refresh(city)
    return city

@app.delete("/cities/{id}")
async def delete_city(id: int, db: db_dependency):
    city = db.query(models.Cities).filter(models.Cities.id == id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    db.delete(city)
    db.commit()
    return {"message": f"City {id} deleted successfully"}

@app.post("/innings/", status_code=status.HTTP_201_CREATED)
async def create_inning(inning: InningBase, db: db_dependency):
    inning_data = inning.dict(exclude_none=True)
    db_inning = models.Innings(**inning_data)
    db.add(db_inning)
    db.commit()
    db.refresh(db_inning)
    return db_inning

@app.get("/innings/")
async def get_all_innings(db: db_dependency):
    return db.query(models.Innings).all()

@app.put("/innings/{inning_id}", status_code=status.HTTP_200_OK)
async def update_inning(inning_id: int, updated_inning: dict, db: db_dependency):
    inning = db.query(models.Innings).filter(models.Innings.inning_id == inning_id).first()
    if not inning:
        raise HTTPException(status_code=404, detail="Inning not found")
    for key, value in updated_inning.items():
        setattr(inning, key, value)
    db.commit()
    db.refresh(inning)
    return inning

@app.delete("/innings/{inning_id}", status_code=status.HTTP_200_OK)
async def delete_inning(inning_id: int, db: db_dependency):
    inning = db.query(models.Innings).filter(models.Innings.inning_id == inning_id).first()
    if not inning:
        raise HTTPException(status_code=404, detail="Inning not found")
    db.delete(inning)
    db.commit()
    return {"message": f"Inning {inning_id} deleted successfully"}

@app.post("/toss/", status_code=status.HTTP_201_CREATED)
async def create_toss(toss: TossBase, db: db_dependency):
    toss_data = toss.dict(exclude_none=True)
    db_toss = models.Toss(**toss_data)
    db.add(db_toss)
    db.commit()
    db.refresh(db_toss)
    return db_toss

@app.get("/toss/", status_code=status.HTTP_200_OK)
async def get_all_tosses(db: db_dependency):
    return db.query(models.Toss).all()

@app.get("/toss/{toss_id}", status_code=status.HTTP_200_OK)
async def get_toss(toss_id: int, db: db_dependency):
    toss = db.query(models.Toss).filter(models.Toss.toss_id == toss_id).first()
    if not toss:
        raise HTTPException(status_code=404, detail="Toss not found")
    return toss

@app.put("/toss/{toss_id}", status_code=status.HTTP_200_OK)
async def update_toss(toss_id: int, updated_toss: dict, db: db_dependency):
    toss = db.query(models.Toss).filter(models.Toss.toss_id == toss_id).first()
    if not toss:
        raise HTTPException(status_code=404, detail="Toss not found")
    for key, value in updated_toss.items():
        setattr(toss, key, value)
    db.commit()
    db.refresh(toss)
    return toss

@app.delete("/toss/{toss_id}", status_code=status.HTTP_200_OK)
async def delete_toss(toss_id: int, db: db_dependency):
    toss = db.query(models.Toss).filter(models.Toss.toss_id == toss_id).first()
    if not toss:
        raise HTTPException(status_code=404, detail="Toss not found")
    db.delete(toss)
    db.commit()
    return {"message": f"Toss {toss_id} deleted successfully"}

@app.post("/appversions/", status_code=status.HTTP_201_CREATED)
async def create_app_version(app_v: AppVersionBase, db: db_dependency):
    app_v_data = app_v.dict(exclude_none=True)
    db_appv = models.app_version_updates(**app_v_data)
    db.add(db_appv)
    db.commit()
    db.refresh(db_appv)
    return db_appv

@app.get("/appversions/", status_code=status.HTTP_200_OK)
async def get_all_app_versions(db: db_dependency):
    return db.query(models.app_version_updates).all()

@app.post("/player_roles/", status_code=status.HTTP_201_CREATED)
async def create_player_role(role: PlayerRoleBase, db: db_dependency):
    role_data = role.dict(exclude_none=True)
    db_role = models.Player_roles(**role_data)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@app.get("/player_roles/", status_code=status.HTTP_200_OK)
async def get_all_player_roles(db: db_dependency):
    return db.query(models.Player_roles).all()

@app.post("/playing_elevens/", status_code=status.HTTP_201_CREATED)
async def create_playing_eleven(eleven: PlayingElevenBase, db: db_dependency):
    eleven_data = eleven.dict(exclude_none=True)
    db_eleven = models.Playing_elevens(**eleven_data)
    db.add(db_eleven)
    db.commit()
    db.refresh(db_eleven)
    return db_eleven

@app.get("/playing_elevens/", status_code=status.HTTP_200_OK)
async def get_all_playing_elevens(db: db_dependency):
    return db.query(models.Playing_elevens).all()

@app.post("/playing_roles/", status_code=status.HTTP_201_CREATED)
async def create_playing_role(role: PlayingRoleBase, db: db_dependency):
    role_data = role.dict(exclude_none=True)
    db_role = models.Playing_roles(**role_data)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@app.get("/playing_roles/", status_code=status.HTTP_200_OK)
async def get_all_playing_roles(db: db_dependency):
    return db.query(models.Playing_roles).all()

@app.post("/qm_balls/", status_code=status.HTTP_201_CREATED)
async def create_qm_ball(ball: QMBallBase, db: db_dependency):
    ball_data = ball.dict(exclude_none=True)
    db_ball = models.QMBall(**ball_data)
    db.add(db_ball)
    db.commit()
    db.refresh(db_ball)
    try:
        if getattr(db_ball, 'is_match_completed', False):
            qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == db_ball.match_id).first()
            if qm:
                qm.match_status = 1
                db.commit()
    except Exception:
        pass
    return db_ball

@app.get("/qm_balls/", status_code=status.HTTP_200_OK)
async def get_all_qm_balls(db: db_dependency):
    return db.query(models.QMBall).all()

@app.get("/qm_balls/{ball_id}", status_code=status.HTTP_200_OK)
async def get_qm_ball(ball_id: int, db: db_dependency):     
    qm_ball = db.query(models.QMBall).filter(models.QMBall.ball_id == ball_id).first()
    if not qm_ball:
        raise HTTPException(status_code=404, detail="QM Ball not found")
    return qm_ball

@app.put("/qm_balls/{ball_id}", status_code=status.HTTP_200_OK)
async def update_qm_ball(ball_id: int, updated_ball: dict, db: db_dependency):
    qm_ball = db.query(models.QMBall).filter(models.QMBall.ball_id == ball_id).first()
    if not qm_ball:
        raise HTTPException(status_code=404, detail="QM Ball not found")
    for key, value in updated_ball.items():
        setattr(qm_ball, key, value)
    db.commit()
    db.refresh(qm_ball)
    # if this update marks the match completed, update QuickMatch status
    try:
        if updated_ball.get('is_match_completed'):
            qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == qm_ball.match_id).first()
            if qm:
                qm.match_status = 1
                db.commit()
    except Exception:
        pass
    return qm_ball

@app.delete("/qm_balls/{ball_id}", status_code=status.HTTP_200_OK)
async def delete_qm_ball(ball_id: int, db: db_dependency):
    qm_ball = db.query(models.QMBall).filter(models.QMBall.ball_id == ball_id).first()
    if not qm_ball:
        raise HTTPException(status_code=404, detail="QM Ball not found")
    db.delete(qm_ball)
    db.commit()
    return {"message": f"QM Ball {ball_id} deleted successfully"}


@app.post("/quickmatches/{qm_match_id}/qm_balls/", status_code=status.HTTP_201_CREATED)
async def create_qm_ball_for_match(qm_match_id: int, ball: QMBallBase, db: db_dependency):
    qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    ball_data = ball.dict(exclude_none=True)
    ball_data['match_id'] = qm_match_id
    db_ball = models.QMBall(**ball_data)
    db.add(db_ball)
    db.commit()
    db.refresh(db_ball)
    try:
        if getattr(db_ball, 'is_match_completed', False):
            qm.match_status = 1
            db.commit()
    except Exception:
        pass
    return db_ball


@app.get("/quickmatches/{qm_match_id}/qm_balls/", status_code=status.HTTP_200_OK)
async def get_qm_balls_for_match(qm_match_id: int, db: db_dependency):
    qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    return db.query(models.QMBall).filter(models.QMBall.match_id == qm_match_id).order_by(models.QMBall.created_at.asc()).all()


@app.get("/quickmatches/{qm_match_id}/qm_balls/latest", status_code=status.HTTP_200_OK)
async def get_latest_qm_ball(qm_match_id: int, db: db_dependency):
    qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    qm_ball = db.query(models.QMBall).filter(models.QMBall.match_id == qm_match_id).order_by(models.QMBall.created_at.desc()).first()
    if not qm_ball:
        raise HTTPException(status_code=404, detail="No QM balls found for this match")
    return qm_ball


@app.get("/quickmatches/{qm_match_id}/summary", status_code=status.HTTP_200_OK)
async def get_qm_match_summary(qm_match_id: int, db: db_dependency):
    # returns the latest aggregated inning_totals / batsman_data / bowler_data available
    qm = db.query(models.QuickMatch).filter(models.QuickMatch.qm_match_id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    latest = db.query(models.QMBall).filter(models.QMBall.match_id == qm_match_id).order_by(models.QMBall.created_at.desc()).first()
    if not latest:
        return {"message": "No balls recorded yet"}
    return {
        "inning_totals": latest.inning_totals,
        "batsman_data": latest.batsman_data,
        "bowler_data": latest.bowler_data,
        "last_ball": latest
    }

@app.post("/share_team/", status_code=status.HTTP_201_CREATED)
async def create_share_team(team: ShareTeamBase, db: db_dependency):
    team_data = team.dict(exclude_none=True)
    db_team = models.Share_team(**team_data)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/share_team/{team_id}", status_code=status.HTTP_200_OK)
async def get_share_team(team_id: int, db: db_dependency):
    share_team = db.query(models.Share_team).filter(models.Share_team.team_id == team_id).first()
    if not share_team:
        raise HTTPException(status_code=404, detail="Share Team not found")
    return share_team

@app.post("/team_master/", status_code=status.HTTP_201_CREATED)
async def create_team_master(team: TeamMasterBase, db: db_dependency):
    team_data = team.dict(exclude_none=True)
    db_team = models.TeamMaster(**team_data)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/team_master/{team_id}", status_code=status.HTTP_200_OK)
async def get_team_master(team_id: int, db: db_dependency):
    team_master = db.query(models.TeamMaster).filter(models.TeamMaster.team_id == team_id).first()
    if not team_master:
        raise HTTPException(status_code=404, detail="Team Master not found")
    return team_master

@app.post("/team_players/", status_code=status.HTTP_201_CREATED)
async def create_team_player(tp: TeamPlayersBase, db: db_dependency):
    tp_data = tp.dict(exclude_none=True)
    db_tp = models.TeamPlayers(**tp_data)
    db.add(db_tp)
    db.commit()
    db.refresh(db_tp)
    return db_tp

@app.get("/team_players/{team_player_id}", status_code=status.HTTP_200_OK)
async def get_team_player(team_player_id: int, db: db_dependency):
    team_player = db.query(models.TeamPlayers).filter(models.TeamPlayers.team_player_id == team_player_id).first()
    if not team_player:
        raise HTTPException(status_code=404, detail="Team Player not found")
    return team_player

@app.post("/team_players_search/", status_code=status.HTTP_201_CREATED)
async def create_team_players_search(search: TeamPlayersSearchBase, db: db_dependency):
    search_data = search.dict(exclude_none=True)
    db_search = models.TeamPlayersSearch(**search_data)
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return db_search

@app.get("/team_players_search/{id}", status_code=status.HTTP_200_OK)
async def get_team_players_search(id: int, db: db_dependency):   
    search = db.query(models.TeamPlayersSearch).filter(models.TeamPlayersSearch.id == id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Team Players Search not found")
    return search

@app.get("/team_players_search/", status_code=status.HTTP_200_OK)
async def get_all_team_players_search(db: db_dependency):
    return db.query(models.TeamPlayersSearch).all()

@app.delete("/team_players_search/{id}", status_code=status.HTTP_200_OK)
async def delete_team_players_search(id: int, db: db_dependency):
    search = db.query(models.TeamPlayersSearch).filter(models.TeamPlayersSearch.id == id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Team Players Search not found")
    db.delete(search)
    db.commit()
    return {"message": f"Team Players Search {id} deleted successfully"}

'''