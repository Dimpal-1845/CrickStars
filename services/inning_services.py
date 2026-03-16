from sqlalchemy.orm import Session
import db
from ..schemas.qm_balls_schema import QMBallBase
from ..schemas.create_qm_schema import CreateQuickMatchSchema as CQMS
from ..db.model import QuickMatch , QMBall as qmb , Innings

class FirstInningService:   
    def start_innings_logic(match_id, striker_bat, non_striker_bat, striker_ball, db):

        match = db.query(QuickMatch).filter(QuickMatch.id == match_id).first()
        if not match:
            return "Match not found"

        if match.status != "toss_done":
            return "Match not ready"

        # validate players exist
        striker = db.query(qmb).filter(qmb.striker_batsman == striker_bat).first()
        non_striker = db.query(qmb).filter(qmb.non_striker_batsman == non_striker_bat).first()
        bowler = db.query(qmb).filter(qmb.striker_bowler == striker_ball).first()

        if not striker or not non_striker or not bowler:
            return "Invalid player id"

        inning = Innings(
            match_id=match_id,
            runs=0,
            wickets=0,
            overs=0,
            balls=0
        )
        
        match.status = "live"

        db.add(inning)  
        db.commit()
        db.refresh(inning)

        return inning
    async def first_inning(self, match_id: int, team_id: int):

            match = CQMS (
                team1_name = self.team1_name,
                team2_name = self.team2_name,
                team1_logo = self.team1_logo,
                team2_logo = self.team2_logo,
                overs = self.overs,
                max_bowlers = self.max_bowlers,
                allow_nb = self.allow_nb,
                allow_wide = self.allow_wide,
                allow_bye = self.allow_bye,
                allow_legbye = self.allow_legbye,
                status = self.status
            )

            self.db.add(match)
            self.db.commit()
            self.db.refresh(match)

            return match
            # Logic to create a first inning record in the database

    def add_ball_logic(ball_data , ball_id : int , db:Session):
        
        if ball_data.match_id is None:
             return "Match not Created"

