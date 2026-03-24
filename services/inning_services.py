from sqlalchemy.orm import Session
from typing import Optional, Dict

# Fix imports
try:
    from db.model import QuickMatch, QMBall, Innings
except ImportError:
    from ..db.model import QuickMatch, QMBall, Innings

try:
    from schemas.qm_balls_schema import QMBallBase
    from schemas.create_qm_schema import CreateQuickMatchSchema as CQMS
except ImportError:
    from ..schemas.qm_balls_schema import QMBallBase
    from ..schemas.create_qm_schema import CreateQuickMatchSchema as CQMS


class InningService:
    """Service for managing innings operations in a quick match."""
    
    @staticmethod
    def start_innings_logic(
        match_id: int,
        striker_bat: str,
        non_striker_bat: str,
        striker_bowl: str,
        db: Session
    ) -> Optional[Dict]:
        """Start an inning for a match with player assignments."""
        
        match = db.query(QuickMatch).filter(QuickMatch.id == match_id).first()
        if not match:
            return {"error": "Match not found", "status": 404}

        if match.match_status != 0:  # 0 = not started, 1 = live, 2 = completed
            return {"error": "Match not in the right state to start inning", "status": 400}

        # Validate that ball records exist for this match
        ball = db.query(QMBall).filter(QMBall.match_id == match_id).first()
        if not ball:
            return {"error": "No ball records found for match", "status": 400}

        # Update the ball with inning starters
        ball.striker_batsman = striker_bat
        ball.non_striker_batsman = non_striker_bat
        ball.striker_bowler = striker_bowl
        ball.current_striker_batsman = striker_bat
        ball.current_non_striker_batsman = non_striker_bat
        ball.current_striker_bowler = striker_bowl
        ball.is_match_start = True
        ball.is_first_inning = True
        
        match.match_status = 1  # Set to live
        
        db.commit()
        db.refresh(ball)
        db.refresh(match)

        return {
            "message": "Inning started successfully",
            "match_id": match_id,
            "striker_batsman": striker_bat,
            "non_striker_batsman": non_striker_bat,
            "striker_bowler": striker_bowl
        }

    @staticmethod
    def add_ball_logic(
        match_id: int,
        ball_data: Dict,
        db: Session
    ) -> Optional[Dict]:
        """Add a new ball delivery to the inning."""
        
        if match_id is None:
            return {"error": "Match ID not provided", "status": 400}

        match = db.query(QuickMatch).filter(QuickMatch.id == match_id).first()
        if not match:
            return {"error": "Match not found", "status": 404}

        if match.match_status != 1:  # Match should be live
            return {"error": "Match is not currently live", "status": 400}

        try:
            # Get the latest ball for this match to use as reference
            latest_ball = db.query(QMBall).filter(
                QMBall.match_id == match_id
            ).order_by(QMBall.created_at.desc()).first()

            if not latest_ball:
                return {"error": "No ball records found for match", "status": 400}

            # Create or update ball with new data
            new_ball = QMBall(
                match_id=match_id,
                striker_batsman=ball_data.get("striker_batsman", latest_ball.striker_batsman),
                non_striker_batsman=ball_data.get("non_striker_batsman", latest_ball.non_striker_batsman),
                striker_bowler=ball_data.get("striker_bowler", latest_ball.striker_bowler),
                non_striker_bowler=ball_data.get("non_striker_bowler", latest_ball.non_striker_bowler),
                current_striker_batsman=ball_data.get("current_striker_batsman", latest_ball.current_striker_batsman),
                current_non_striker_batsman=ball_data.get("current_non_striker_batsman", latest_ball.current_non_striker_batsman),
                current_striker_bowler=ball_data.get("current_striker_bowler", latest_ball.current_striker_bowler),
                current_non_striker_bowler=ball_data.get("current_non_striker_bowler", latest_ball.current_non_striker_bowler),
                team_name=ball_data.get("team_name", latest_ball.team_name),
                run_scored=ball_data.get("run_scored", 0),
                is_no_ball=ball_data.get("is_no_ball", 0),
                is_wide_ball=ball_data.get("is_wide_ball", 0),
                is_bye=ball_data.get("is_bye", 0),
                is_leg_bye=ball_data.get("is_leg_bye", 0),
                is_four=ball_data.get("is_four", 0),
                is_six=ball_data.get("is_six", 0),
                is_out=ball_data.get("is_out", 0),
                out_type=ball_data.get("out_type"),
                over_counter=ball_data.get("over_counter", latest_ball.over_counter),
                is_over_completed=ball_data.get("is_over_completed", 0),
                is_inning_completed=ball_data.get("is_inning_completed", 0),
                is_first_inning=ball_data.get("is_first_inning", True),
                is_second_inning=ball_data.get("is_second_inning", False),
            )
            
            db.add(new_ball)
            db.commit()
            db.refresh(new_ball)

            return {
                "message": "Ball added successfully",
                "ball_id": new_ball.ball_id,
                "match_id": match_id
            }

        except Exception as e:
            db.rollback()
            return {"error": f"Failed to add ball: {str(e)}", "status": 500}

    @staticmethod
    def end_inning(match_id: int, db: Session) -> Optional[Dict]:
        """End the current inning."""
        
        match = db.query(QuickMatch).filter(QuickMatch.id == match_id).first()
        if not match:
            return {"error": "Match not found", "status": 404}

        # Update all balls for this inning to mark inning as completed
        balls = db.query(QMBall).filter(QMBall.match_id == match_id).all()
        for ball in balls:
            ball.is_inning_completed = True
        
        db.commit()

        return {
            "message": "Inning ended successfully",
            "match_id": match_id
        }