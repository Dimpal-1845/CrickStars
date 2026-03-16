import db.model as model
from db.database import get_db
from schemas.create_qm_schema import CreateQuickMatchSchema as CQMS
from fastapi import APIRouter, Depends, HTTPException, status
from db.model import QuickMatch , QMBall
from sqlalchemy.orm import Session  
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
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
'''
@router.get("/quickmatchs/" , status_code=status.HTTP_200_OK)
def get_all_quickmatchs(db: Session = Depends(get_db)):
    return db.query(model.QuickMatch).all()


@router.put("/quickmatchs/{qm_match_id}" , status_code=status.HTTP_200_OK)
def update_quickmatch(qm_match_id: int, update_quickmatch: QuickMatchBase, db: Session = Depends(get_db)):
    qm = db.query(model.QuickMatch).filter(model.QuickMatch.id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    update_data = update_quickmatch.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(qm, key, value)
    db.commit()
    db.refresh(qm)
    return qm'''


@router.delete("/quickmatchs/{qm_match_id}" , status_code=status.HTTP_200_OK)
def delete_quickmatch(qm_match_id: int, db: Session = Depends(get_db)):
    qm = db.query(model.QuickMatch).filter(model.QuickMatch.id == qm_match_id).first()
    if not qm:
        raise HTTPException(status_code=404, detail="QuickMatch not found")
    db.delete(qm)
    db.commit()
    return {"message": f"QuickMatch record {qm_match_id} deleted successfully"}

