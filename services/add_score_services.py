from typing import Dict
from sqlalchemy.orm import Session

# Fix the import path - assuming the schema exists
try:
    from schemas.qm_balls_schema import QMBallBase as qmb
except ImportError:
    # Fallback if import path structure is different
    from ..schemas.qm_balls_schema import QMBallBase as qmb

try:
    from db.model import QMBall as QMBallModel, QuickMatch
except ImportError:
    from ..db.model import QMBall as QMBallModel, QuickMatch

def _overs_to_balls(over_float: float) -> int:
    overs = int(over_float)
    balls = int(round((over_float - overs) * 10))
    return overs * 6 + balls


def _balls_to_over_float(balls: int) -> float:
    return float(f"{balls // 6}.{balls % 6}")

def _empty_score(is_dev_record: bool) -> qmb:
    return qmb(
        is_match_start=0,
        run_scored=0,
        is_no_ball=0,
        is_wide_ball=0,
        is_bye=0,
        is_leg_bye=0,
        is_four=0,
        is_six=0,
        is_out=0,
        over_counter=0.00,
        is_over_completed=0,
        is_inning_completed=0,
        is_match_completed=0,
        is_first_inning=0,
        is_second_inning=0,
        is_deve_record=1 if is_dev_record else 0,
    )


def _load_current_score(db: Session, match_id: int, is_dev_record: bool) -> qmb:
    if not db or not match_id:
        return _empty_score(is_dev_record)

    row = (
        db.query(QMBallModel)
        .filter(QMBallModel.match_id == match_id)
        .order_by(QMBallModel.id.desc())
        .first()
    )

    if not row:
        return _empty_score(is_dev_record)

    return qmb(
        run_scored=row.runs_scored or 0,
        over_counter=row.over_counter or 0.00,
        is_first_inning=row.is_first_inning,
        is_second_inning=row.is_second_inning,
        is_deve_record=row.is_deve_record,
        current_striker_batsman=row.current_striker_batsman or row.striker_batsman,
        current_non_striker_batsman=row.current_non_striker_batsman or row.non_striker_batsman,
        current_striker_bowler=row.current_striker_bowler or row.striker_bowler,
        current_non_striker_bowler=row.current_non_striker_bowler or row.non_striker_bowler,
    )

async def ball_count(
    is_dev_record: bool, 
    event: Dict,
    no_of_overs: int = 5,
    no_of_bowlers: int = 1,
    db: Session | None = None,
):
    match_id = event.get("match_id") or event.get("matchId")
    score = _load_current_score(db, match_id, is_dev_record)

    run_before = score.run_scored or 0
    over_counter = score.over_counter or 0.00 
    balls_bowled = _overs_to_balls(over_counter)
    total_balls_allowed = no_of_overs * 6

    runs = int(event.get("runs", 0))
    is_wide = 1 if event.get("is_wide") or event.get("isWide") else 0
    is_no_ball = 1 if event.get("is_no_ball") or event.get("isNoBall") else 0
    is_bye = 1 if event.get("is_bye") or event.get("isBye") else 0
    is_leg_bye = 1 if event.get("is_leg_bye") or event.get("isLegBye") else 0
    is_four = 1 if runs == 4 else 0
    is_six = 1 if runs == 6 else 0
    is_out = 1 if event.get("is_out") or event.get("isOut") else 0
    
    if is_out:
        swap_batsmen = False
    extra_runs = 0
    if is_wide: 
        extra_runs += 1
    if is_no_ball:
        extra_runs += 1

    new_total_runs = run_before + runs + extra_runs

    legal_delivery = not (is_wide or is_no_ball)

    if is_bye or is_leg_bye:
        legal_delivery = True

    if legal_delivery:
        balls_bowled += 1

    new_over_counter = _balls_to_over_float(balls_bowled)

    is_over_completed = 1 if (balls_bowled > 0 and (balls_bowled % 6 == 0)) else 0

    is_inning_completed = 1 if (balls_bowled >= total_balls_allowed) else 0

    swap_batsmen = False
    swap_bowlers = False

    if no_of_bowlers == 2:
        if is_wide:
            swap_batsmen = False
            swap_bowlers = False
        elif is_no_ball:
            swap_batsmen = (runs % 2 == 1)
            swap_bowlers = False
        elif is_four or is_six:
            swap_batsmen = False
            swap_bowlers = False
        else:
            if runs % 2 == 1:
                swap_batsmen = True
                swap_bowlers = True
            else:
                swap_batsmen = False
                swap_bowlers = True
    else:
        if is_wide:
            swap_batsmen = False
            swap_bowlers = False
        elif is_no_ball:
            swap_batsmen = (runs % 2 == 1)
            swap_bowlers = False
        else:
            swap_batsmen = (runs % 2 == 1)
            swap_bowlers = False

    cur_striker_batsman = score.current_striker_batsman or (score.striker_batsman if hasattr(score, 'striker_batsman') else None)
    cur_non_striker_batsman = score.current_non_striker_batsman or (score.non_striker_batsman if hasattr(score, 'non_striker_batsman') else None)
    cur_striker_bowler = score.current_striker_bowler or (score.striker_bowler if hasattr(score, 'striker_bowler') else None)
    cur_non_striker_bowler = score.current_non_striker_bowler or (score.non_striker_bowler if hasattr(score, 'non_striker_bowler') else None)

    if swap_batsmen and cur_striker_batsman and cur_non_striker_batsman:
        cur_striker_batsman, cur_non_striker_batsman = cur_non_striker_batsman, cur_striker_batsman

    if swap_bowlers and cur_striker_bowler and cur_non_striker_bowler:
        cur_striker_bowler, cur_non_striker_bowler = cur_non_striker_bowler, cur_striker_bowler

    return qmb(
        run_scored=new_total_runs,
        is_no_ball=is_no_ball,
        is_wide_ball=is_wide,
        is_bye=is_bye,
        is_leg_bye=is_leg_bye,
        is_four=is_four,
        is_six=is_six,
        is_out=is_out,
        over_counter=new_over_counter,
        is_over_completed=is_over_completed,
        is_inning_completed=is_inning_completed,
        is_match_completed=0,
        current_striker_batsman=cur_striker_batsman,
        current_non_striker_batsman=cur_non_striker_batsman,
        current_striker_bowler=cur_striker_bowler,
        current_non_striker_bowler=cur_non_striker_bowler,
        is_first_inning=score.is_first_inning if score else 0,
        is_second_inning=score.is_second_inning if score else 0,
        is_deve_record=score.is_deve_record if getattr(score, "is_deve_record", None) is not None else  (1 if is_dev_record else 0)
    )

async def finalize_match_score(
        is_dev_recored: bool,
        db: Session,
        match_id: int
):
    """Complete the current match and return final score."""
    score = _load_current_score(db, match_id, is_dev_recored)
    if not score or score.is_match_completed:
        return score
    
    # Mark match as completed
    final_score = qmb(
        run_scored=score.run_scored,
        over_counter=score.over_counter,
        is_match_completed=1,
        is_inning_completed=1,
        is_over_completed=score.is_over_completed,
        is_first_inning=score.is_first_inning,
        is_second_inning=score.is_second_inning,
        current_striker_batsman=score.current_striker_batsman,
        current_non_striker_batsman=score.current_non_striker_batsman,
        current_striker_bowler=score.current_striker_bowler,
        current_non_striker_bowler=score.current_non_striker_bowler,
        is_deve_record=score.is_deve_record
    )
    
    # Update the match record in database to mark as completed
    match = db.query(QuickMatch).filter(QuickMatch.id == match_id).first()
    if match:
        match.match_status = 2  # 2 = completed
        db.commit()
    
    return final_score