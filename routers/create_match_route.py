import db.model as model
from db.database import get_db
from schemas.create_qm_schema import CreateQuickMatchSchema as CQMS, UpdateQuickMatchSchema
from fastapi import APIRouter, Depends, HTTPException, status, Body
from db.model import QuickMatch , QMBall
from sqlalchemy.orm import Session  
from typing import Annotated, Optional, Dict
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

# services
try:
    from services.add_score_services import ball_count, finalize_match_score
except ImportError:
    # fallback for relative import contexts
    from ..services.add_score_services import ball_count, finalize_match_score

# Import services if available
try:
    from services.inning_services import InningService
except ImportError:
    InningService = None

router = APIRouter(prefix="/matches", tags=["matches"])

templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]

def _model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

@router.post("/quickmatches/", status_code=status.HTTP_201_CREATED)
async def create_quick_match(payload: CQMS, db: db_dependency):
    try:
        data = payload.dict(exclude_unset=True, exclude_none=True)

        # fields that belong to qm_match
        qm_fields = {
            "team1_name",
            "team1_image",
            "team2_name",
            "team2_image",
            "match_settings",
            "toss_info",
            # add any other QuickMatch fields you want to accept from the payload
        }

        qm_data = {k: v for k, v in data.items() if k in qm_fields}

        # ensure required non-null DB fields have defaults if not provided
        qm_data.setdefault("match_transfer_user_id", 0)
        qm_data.setdefault("player_id", 0)

        db_qm = QuickMatch(**qm_data)
        db.add(db_qm)
        db.flush()

        # fields that belong to qm_balls (request uses underscore names)
        ball_fields = {
            "striker_batsman",
            "non_striker_batsman",
            "striker_bowler",
            "non_striker_bowler",
            "team_name",
        }

        # Map underscore keys from request to model attribute names where they differ
        qm_ball_data = {"match_id": db_qm.id}
        for k in ball_fields:
            if k in data:
                # special mapping for non_striker_* -> nonstriker_* model attrs
                if k == "non_striker_batsman":
                    qm_ball_data["non_striker_batsman"] = data[k]
                elif k == "non_striker_bowler":
                    qm_ball_data["non_striker_bowler"] = data[k]
                elif k == "run_scored":
                    # accept legacy key name and map to the model attribute
                    qm_ball_data["runs_scored"] = data[k]
                elif k == "out_player_id":
                    # legacy API may send an id; store as string in out_player_name column
                    qm_ball_data["out_player_name"] = str(data[k]) if data[k] is not None else None
                elif k == "out_player_name":
                    qm_ball_data["out_player_name"] = data[k]
                else:
                    qm_ball_data[k] = data[k]

        # fill required fields with safe defaults to avoid NOT NULL failures
        qm_ball_data.setdefault("striker_batsman", "")
        qm_ball_data.setdefault("non_striker_batsman", "")
        qm_ball_data.setdefault("striker_bowler", "")
        qm_ball_data.setdefault("non_striker_bowler", qm_ball_data.get("striker_bowler", ""))
        qm_ball_data.setdefault("team_name", qm_data.get("team1_name", ""))

        # set sensible defaults for required current_* fields if not provided
        qm_ball_data.setdefault("current_striker_batsman", qm_ball_data.get("striker_batsman", ""))
        qm_ball_data.setdefault("current_non_striker_batsman", qm_ball_data.get("non_striker_batsman", ""))
        qm_ball_data.setdefault("current_striker_bowler", qm_ball_data.get("striker_bowler", ""))
        qm_ball_data.setdefault("current_non_striker_bowler", qm_ball_data.get("non_striker_bowler", ""))
        # ensure required non-null DB columns have safe defaults

        db_qm_ball = QMBall(**qm_ball_data)
        db.add(db_qm_ball)

        db.commit()

        db.refresh(db_qm)
        db.refresh(db_qm_ball)

        return {
            "message": "Quick Match created successfully",
            "match_id": db_qm.id
        }

        # Validate the input data
        '''if payload.overs <= 0:
            raise HTTPException(status_code=400, detail="Overs must be greater than 0")
        if payload.no_of_bowlers <= 0:
            raise HTTPException(status_code=400, detail="Number of bowlers must be greater than 0")
        if payload.powerplay_overs < 0:
            raise HTTPException(status_code=400, detail="Powerplay overs cannot be negative")'''

    except HTTPException:
        # allow HTTPExceptions to propagate unchanged (404 etc.)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create quick match: {str(e)}"
        )

@router.get("/quickmatches/{qm_match_id}", status_code=status.HTTP_200_OK)
async def read_quick_match(qm_match_id: int, db: db_dependency):
    qm = db.query(model.QuickMatch).filter(model.QuickMatch.id == qm_match_id).first()
    if qm is None:
        raise HTTPException(status_code=404, detail="Quick match not found")
    data = _model_to_dict(qm)
    data["match_id"] = qm.id

    latest_ball = (
        db.query(model.QMBall)
        .filter(model.QMBall.match_id == qm_match_id)
        .order_by(model.QMBall.created_at.desc())
        .first()
    )
    if latest_ball:
        data.update(
            {
                "striker_batsman": latest_ball.striker_batsman,
                "non_striker_batsman": latest_ball.non_striker_batsman,
                "striker_bowler": latest_ball.striker_bowler,
                "non_striker_bowler": latest_ball.non_striker_bowler,
                "current_striker_batsman": latest_ball.current_striker_batsman,
                "current_non_striker_batsman": latest_ball.current_non_striker_batsman,
                "current_striker_bowler": latest_ball.current_striker_bowler,
                "current_non_striker_bowler": latest_ball.current_non_striker_bowler,
                "inning_totals": latest_ball.inning_totals,
                "batsman_data": latest_ball.batsman_data,
                "bowler_data": latest_ball.bowler_data,
            }
        )
    return data


@router.get("/quickmatchs/", status_code=status.HTTP_200_OK)
async def get_all_quickmatchs(db: db_dependency):
    """Get all quick matches from the database."""
    try:
        matches = db.query(model.QuickMatch).order_by(model.QuickMatch.created_at.desc()).all()

        result = []
        for match in matches:
            latest_ball = (
                db.query(model.QMBall)
                .filter(model.QMBall.match_id == match.id)
                .order_by(model.QMBall.created_at.desc())
                .first()
            )

            score = '0/0'
            overs_played = 0.0
            if latest_ball:
                runs = latest_ball.run_scored or 0
                wickets = 0
                if latest_ball.inning_totals and isinstance(latest_ball.inning_totals, dict):
                    wickets = latest_ball.inning_totals.get('wickets', 0) or 0
                score = f"{runs}/{wickets}"
                overs_played = latest_ball.over_counter or 0.0

            result.append({
                'id': match.id,
                'team1_name': match.team1_name,
                'team1_image': match.team1_image,
                'team2_name': match.team2_name,
                'team2_image': match.team2_image,
                'match_status': match.match_status,
                'created_at': match.created_at,
                'score': score,
                'overs_played': overs_played,
                # fallback stadium if in settings
                'stadium': (match.match_settings or {}).get('stadium') if isinstance(match.match_settings, dict) else None,
            })

        return {"matches": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matches: {str(e)}"
        )


@router.put("/quickmatchs/{qm_match_id}", status_code=status.HTTP_200_OK)
async def update_quickmatch(
    qm_match_id: int, 
    update_data: UpdateQuickMatchSchema, 
    db: db_dependency
):
    """Update a quick match by ID."""
    try:
        qm = db.query(model.QuickMatch).filter(model.QuickMatch.id == qm_match_id).first()
        if not qm:
            raise HTTPException(status_code=404, detail="QuickMatch not found")
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(qm, key, value)
        
        db.commit()
        db.refresh(qm)
        
        return {
            "message": "Quick Match updated successfully",
            "match": _model_to_dict(qm)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update quick match: {str(e)}"
        )


@router.delete("/quickmatchs/{qm_match_id}", status_code=status.HTTP_200_OK)
async def delete_quickmatch(qm_match_id: int, db: db_dependency):
    """Delete a quick match by ID."""
    try:
        qm = db.query(model.QuickMatch).filter(model.QuickMatch.id == qm_match_id).first()
        if not qm:
            raise HTTPException(status_code=404, detail="QuickMatch not found")
        db.delete(qm)
        db.commit()
        return {"message": f"QuickMatch record {qm_match_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete quick match: {str(e)}"
        )


# Inning Management Endpoints
@router.post("/quickmatches/{qm_match_id}/start-inning", status_code=status.HTTP_200_OK)
async def start_inning(
    qm_match_id: int,
    striker_batsman: str,
    non_striker_batsman: str,
    striker_bowler: str,
    db: db_dependency
):
    """Start an inning for a quick match."""
    if not InningService:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Inning service not available"
        )
    
    result = InningService.start_innings_logic(
        match_id=qm_match_id,
        striker_bat=striker_batsman,
        non_striker_bat=non_striker_batsman,
        striker_bowl=striker_bowler,
        db=db
    )
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result.get("error")
        )
    
    return result


@router.post("/quickmatches/{qm_match_id}/add-ball", status_code=status.HTTP_201_CREATED)
async def add_ball(
    qm_match_id: int,
    ball_data: Dict,
    db: db_dependency
):
    """Add a ball delivery to a match."""
    if not InningService:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Inning service not available"
        )
    
    result = InningService.add_ball_logic(
        match_id=qm_match_id,
        ball_data=ball_data,
        db=db
    )
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result.get("error")
        )
    
    return result


@router.post("/quickmatches/{qm_match_id}/end-inning", status_code=status.HTTP_200_OK)
async def end_inning(qm_match_id: int, db: db_dependency):
    """End the current inning."""
    if not InningService:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Inning service not available"
        )
    
    result = InningService.end_inning(match_id=qm_match_id, db=db)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result.get("error")
        )
    
    return result


def _get_quickmatch(db: Session, qm_match_id: int) -> QuickMatch:
    qm = db.query(QuickMatch).filter(QuickMatch.id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="Match not found")
    return qm


def _get_latest_ball(db: Session, qm_match_id: int) -> Optional[QMBall]:
    return (
        db.query(QMBall)
        .filter(QMBall.match_id == qm_match_id)
        .order_by(QMBall.created_at.desc())
        .first()
    )


@router.get("/quickmatches/{qm_match_id}/score", status_code=status.HTTP_200_OK)
async def get_qm_score(qm_match_id: int, db: db_dependency):
    """Get the latest scoring snapshot for a quick match."""
    _get_quickmatch(db, qm_match_id)
    latest_ball = _get_latest_ball(db, qm_match_id)
    if not latest_ball:
        return {"message": "No score yet"}

    return {
        "match_id": qm_match_id,
        "run_scored": latest_ball.run_scored,
        "over_counter": latest_ball.over_counter,
        "is_over_completed": latest_ball.is_over_completed,
        "is_inning_completed": latest_ball.is_inning_completed,
        "is_match_completed": latest_ball.is_match_completed,
        "striker_batsman": latest_ball.current_striker_batsman,
        "non_striker_batsman": latest_ball.current_non_striker_batsman,
        "striker_bowler": latest_ball.current_striker_bowler,
        "non_striker_bowler": latest_ball.current_non_striker_bowler,
        "inning_totals": latest_ball.inning_totals,
        "batsman_data": latest_ball.batsman_data,
        "bowler_data": latest_ball.bowler_data,
    }


@router.post("/quickmatches/{qm_match_id}/add-score", status_code=status.HTTP_201_CREATED)
async def add_score(
    qm_match_id: int,
    score_event: Dict,
    db: db_dependency
):
    """Add scoring event (ball) to the match."""
    match = _get_quickmatch(db, qm_match_id)

    # ensure match has settings for overs/bowlers
    no_of_overs = 5
    no_of_bowlers = 1
    if match.match_settings and isinstance(match.match_settings, dict):
        no_of_overs = int(match.match_settings.get("overs") or no_of_overs)
        no_of_bowlers = int(match.match_settings.get("no_of_bowlers") or no_of_bowlers)

    # Ensure match_id is part of the event for compatibility
    score_event = {**score_event, "match_id": qm_match_id}

    computed = await ball_count(
        is_dev_record=False,
        event=score_event,
        no_of_overs=no_of_overs,
        no_of_bowlers=no_of_bowlers,
        db=db,
    )

    # Persist computed ball state
    ball = QMBall(
        match_id=qm_match_id,
        striker_batsman=computed.current_striker_batsman or "",
        non_striker_batsman=computed.current_non_striker_batsman or "",
        striker_bowler=computed.current_striker_bowler or "",
        non_striker_bowler=computed.current_non_striker_bowler or "",
        current_striker_batsman=computed.current_striker_batsman or "",
        current_non_striker_batsman=computed.current_non_striker_batsman or "",
        current_striker_bowler=computed.current_striker_bowler or "",
        current_non_striker_bowler=computed.current_non_striker_bowler or "",
        team_name=score_event.get("team_name") or match.team1_name or "",
        run_scored=computed.run_scored,
        is_no_ball=computed.is_no_ball,
        is_wide_ball=computed.is_wide_ball,
        is_bye=computed.is_bye,
        is_leg_bye=computed.is_leg_bye,
        is_four=computed.is_four,
        is_six=computed.is_six,
        is_out=computed.is_out,
        out_type=score_event.get("out_type"),
        over_counter=computed.over_counter,
        is_over_completed=computed.is_over_completed,
        is_inning_completed=computed.is_inning_completed,
        is_match_completed=computed.is_match_completed,
        is_first_inning=computed.is_first_inning,
        is_second_inning=computed.is_second_inning,
        inning_totals=getattr(computed, "inning_totals", None),
        batsman_data=getattr(computed, "batsman_data", None),
        bowler_data=getattr(computed, "bowler_data", None),
    )

    db.add(ball)
    if getattr(computed, "is_match_completed", 0):
        match.match_status = 2
    db.commit()
    db.refresh(ball)
    db.refresh(match)

    return {
        "message": "Score added successfully",
        "match_id": qm_match_id,
        "ball_id": ball.ball_id,
        "is_match_completed": computed.is_match_completed,
        "is_inning_completed": computed.is_inning_completed,
    }


@router.post("/quickmatches/{qm_match_id}/swap-batsman", status_code=status.HTTP_200_OK)
async def swap_batsman(qm_match_id: int, db: db_dependency):
    """Swap striker and non-striker batsman for the current ball."""
    _get_quickmatch(db, qm_match_id)
    latest_ball = _get_latest_ball(db, qm_match_id)
    if not latest_ball:
        raise HTTPException(status_code=404, detail="No ball record to swap batsmen")

    new_ball = QMBall(
        match_id=qm_match_id,
        striker_batsman=latest_ball.striker_batsman,
        non_striker_batsman=latest_ball.non_striker_batsman,
        striker_bowler=latest_ball.striker_bowler,
        non_striker_bowler=latest_ball.non_striker_bowler,
        current_striker_batsman=latest_ball.current_non_striker_batsman,
        current_non_striker_batsman=latest_ball.current_striker_batsman,
        current_striker_bowler=latest_ball.current_striker_bowler,
        current_non_striker_bowler=latest_ball.current_non_striker_bowler,
        run_scored=latest_ball.run_scored,
        is_no_ball=latest_ball.is_no_ball,
        is_wide_ball=latest_ball.is_wide_ball,
        is_bye=latest_ball.is_bye,
        is_leg_bye=latest_ball.is_leg_bye,
        is_four=latest_ball.is_four,
        is_six=latest_ball.is_six,
        is_out=latest_ball.is_out,
        out_type=latest_ball.out_type,
        over_counter=latest_ball.over_counter,
        is_over_completed=latest_ball.is_over_completed,
        is_inning_completed=latest_ball.is_inning_completed,
        is_match_completed=latest_ball.is_match_completed,
        team_name=latest_ball.team_name,
        inning_totals=latest_ball.inning_totals,
        batsman_data=latest_ball.batsman_data,
        bowler_data=latest_ball.bowler_data,
    )

    db.add(new_ball)
    db.commit()
    db.refresh(new_ball)

    return {
        "message": "Batsmen swapped successfully",
        "ball_id": new_ball.ball_id,
    }


@router.post("/quickmatches/{qm_match_id}/swap-bowler", status_code=status.HTTP_200_OK)
async def swap_bowler(qm_match_id: int, db: db_dependency):
    """Swap striker and non-striker bowlers for the current ball."""
    _get_quickmatch(db, qm_match_id)
    latest_ball = _get_latest_ball(db, qm_match_id)
    if not latest_ball:
        raise HTTPException(status_code=404, detail="No ball record to swap bowlers")

    new_ball = QMBall(
        match_id=qm_match_id,
        striker_batsman=latest_ball.striker_batsman,
        non_striker_batsman=latest_ball.non_striker_batsman,
        striker_bowler=latest_ball.striker_bowler,
        non_striker_bowler=latest_ball.non_striker_bowler,
        current_striker_batsman=latest_ball.current_striker_batsman,
        current_non_striker_batsman=latest_ball.current_non_striker_batsman,
        current_striker_bowler=latest_ball.current_non_striker_bowler,
        current_non_striker_bowler=latest_ball.current_striker_bowler,
        run_scored=latest_ball.run_scored,
        is_no_ball=latest_ball.is_no_ball,
        is_wide_ball=latest_ball.is_wide_ball,
        is_bye=latest_ball.is_bye,
        is_leg_bye=latest_ball.is_leg_bye,
        is_four=latest_ball.is_four,
        is_six=latest_ball.is_six,
        is_out=latest_ball.is_out,
        out_type=latest_ball.out_type,
        over_counter=latest_ball.over_counter,
        is_over_completed=latest_ball.is_over_completed,
        is_inning_completed=latest_ball.is_inning_completed,
        is_match_completed=latest_ball.is_match_completed,
        team_name=latest_ball.team_name,
        inning_totals=latest_ball.inning_totals,
        batsman_data=latest_ball.batsman_data,
        bowler_data=latest_ball.bowler_data,
    )

    db.add(new_ball)
    db.commit()
    db.refresh(new_ball)

    return {
        "message": "Bowlers swapped successfully",
        "ball_id": new_ball.ball_id,
    }


@router.post("/quickmatches/{qm_match_id}/start-second-inning", status_code=status.HTTP_200_OK)
async def start_second_inning(
    qm_match_id: int,
    striker_batsman: str,
    non_striker_batsman: str,
    striker_bowler: str,
    db: db_dependency,
):
    """Start the second inning for a quick match."""
    match = _get_quickmatch(db, qm_match_id)

    # set match live if not already
    match.match_status = 1

    new_ball = QMBall(
        match_id=qm_match_id,
        striker_batsman=striker_batsman,
        non_striker_batsman=non_striker_batsman,
        striker_bowler=striker_bowler,
        non_striker_bowler="",
        current_striker_batsman=striker_batsman,
        current_non_striker_batsman=non_striker_batsman,
        current_striker_bowler=striker_bowler,
        current_non_striker_bowler="",
        run_scored=0,
        is_no_ball=0,
        is_wide_ball=0,
        is_bye=0,
        is_leg_bye=0,
        is_four=0,
        is_six=0,
        is_out=0,
        over_counter=0.0,
        is_over_completed=0,
        is_inning_completed=0,
        is_match_completed=0,
        team_name=match.team2_name or "",
        is_first_inning=0,
        is_second_inning=1,
    )
    db.add(new_ball)
    db.commit()
    db.refresh(new_ball)
    db.refresh(match)

    return {
        "message": "Second inning started",
        "match_id": qm_match_id,
        "ball_id": new_ball.ball_id,
    }


# Legacy aliases (Postman-style endpoint compatibility)
legacy_router = APIRouter(tags=["legacy"])

@legacy_router.post("/create-match", status_code=status.HTTP_201_CREATED)
async def create_match_alias(payload: CQMS, db: db_dependency):
    return await create_quick_match(payload, db)

@legacy_router.post("/list-match", status_code=status.HTTP_200_OK)
async def list_match_alias(db: db_dependency, body: dict = Body(None)):
    return await get_all_quickmatchs(db)

@legacy_router.post("/update-match", status_code=status.HTTP_200_OK)
async def update_match_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    update_data = {k: v for k, v in body.items() if k != "match_id"}
    return await update_quickmatch(match_id, UpdateQuickMatchSchema(**update_data), db)

@legacy_router.post("/delete-match", status_code=status.HTTP_200_OK)
async def delete_match_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await delete_quickmatch(match_id, db)

@legacy_router.post("/start-match", status_code=status.HTTP_200_OK)
async def start_match_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await start_inning(
        qm_match_id=match_id,
        striker_batsman=body.get("striker_batsman", ""),
        non_striker_batsman=body.get("non_striker_batsman", ""),
        striker_bowler=body.get("striker_bowler", ""),
        db=db,
    )

@legacy_router.post("/add-score", status_code=status.HTTP_201_CREATED)
async def add_score_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await add_score(match_id, body, db)

@legacy_router.post("/get-score", status_code=status.HTTP_200_OK)
async def get_score_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await get_qm_score(match_id, db)

@legacy_router.post("/swap-batsman", status_code=status.HTTP_200_OK)
async def swap_batsman_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await swap_batsman(match_id, db)

@legacy_router.post("/swap-bowler", status_code=status.HTTP_200_OK)
async def swap_bowler_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await swap_bowler(match_id, db)

@legacy_router.post("/end-inning", status_code=status.HTTP_200_OK)
async def end_inning_alias(db: db_dependency, body: dict = Body(...)):
    match_id = body.get("match_id")
    if not match_id:
        raise HTTPException(status_code=400, detail="match_id is required")
    return await end_inning(match_id, db)

