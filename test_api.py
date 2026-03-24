import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db.database import Base, get_db
from db.model import QuickMatch, QMBall

# Use SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestMainEndpoints:
    """Test main website endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "CrickStars API"
    
    def test_index_page(self):
        """Test main dashboard page"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Quick Match" in response.text or "text/html" in response.headers.get("content-type", "")


class TestQuickMatchCRUD:
    """Test Quick Match CRUD operations"""
    
    def setup_method(self):
        """Clear database before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_create_quick_match_success(self):
        """Test successful match creation"""
        payload = {
            "team1_name": "Team A",
            "team1_image": "https://example.com/teamA.jpg",
            "team2_name": "Team B",
            "team2_image": "https://example.com/teamB.jpg",
            "striker_batsman": "Batsman1",
            "non_striker_batsman": "Batsman2",
            "striker_bowler": "Bowler1",
            "match_settings": {"overs": 5},
            "toss_info": {"winner": "Team A"}
        }
        
        response = client.post("/matches/quickmatches/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "match_id" in data
        assert data["message"] == "Quick Match created successfully"
    
    def test_create_quick_match_missing_required_field(self):
        """Test match creation with missing required field"""
        payload = {
            "team1_image": "https://example.com/teamA.jpg",
            "team2_name": "Team B",
            "team2_image": "https://example.com/teamB.jpg"
        }
        
        response = client.post("/matches/quickmatches/", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_all_matches_empty(self):
        """Test getting matches when database is empty"""
        response = client.get("/matches/quickmatchs/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["matches"] == []
    
    def test_get_all_matches_with_data(self):
        """Test getting all matches with data"""
        # Create a match
        payload = {
            "team1_name": "Team A",
            "team2_name": "Team B",
            "striker_batsman": "Batsman1",
            "non_striker_batsman": "Batsman2",
            "striker_bowler": "Bowler1"
        }
        create_response = client.post("/matches/quickmatches/", json=payload)
        match_id = create_response.json()["match_id"]
        
        # Get all matches
        response = client.get("/matches/quickmatchs/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["matches"]) == 1
    
    def test_get_single_match_success(self):
        """Test retrieving a single match"""
        # Create a match first
        payload = {
            "team1_name": "Strikers",
            "team2_name": "Royals",
            "striker_batsman": "Player1",
            "non_striker_batsman": "Player2",
            "striker_bowler": "Bowler1"
        }
        create_response = client.post("/matches/quickmatches/", json=payload)
        match_id = create_response.json()["match_id"]
        
        # Get the match
        response = client.get(f"/matches/quickmatches/{match_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["team1_name"] == "Strikers"
        assert data["team2_name"] == "Royals"
        assert data["striker_batsman"] == "Player1"
    
    def test_get_match_not_found(self):
        """Test getting non-existent match"""
        response = client.get("/matches/quickmatches/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_match_success(self):
        """Test updating match"""
        # Create match
        payload = {
            "team1_name": "Team A",
            "team2_name": "Team B",
            "striker_batsman": "Batsman1",
            "non_striker_batsman": "Batsman2",
            "striker_bowler": "Bowler1"
        }
        create_response = client.post("/matches/quickmatches/", json=payload)
        match_id = create_response.json()["match_id"]
        
        # Update match
        update_payload = {
            "winning_team": "Team A",
            "win_by": "5 wickets",
            "match_status": 2
        }
        response = client.put(f"/matches/quickmatchs/{match_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Quick Match updated successfully"
        assert data["match"]["winning_team"] == "Team A"
    
    def test_update_nonexistent_match(self):
        """Test updating non-existent match"""
        update_payload = {"winning_team": "Team A"}
        response = client.put("/matches/quickmatchs/9999", json=update_payload)
        assert response.status_code == 404
    
    def test_delete_match_success(self):
        """Test deleting a match"""
        # Create match
        payload = {
            "team1_name": "Team A",
            "team2_name": "Team B",
            "striker_batsman": "Batsman1",
            "non_striker_batsman": "Batsman2",
            "striker_bowler": "Bowler1"
        }
        create_response = client.post("/matches/quickmatches/", json=payload)
        match_id = create_response.json()["match_id"]
        
        # Delete match
        response = client.delete(f"/matches/quickmatchs/{match_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        verify_response = client.get(f"/matches/quickmatches/{match_id}")
        assert verify_response.status_code == 404
    
    def test_delete_nonexistent_match(self):
        """Test deleting non-existent match"""
        response = client.delete("/matches/quickmatchs/9999")
        assert response.status_code == 404


class TestInningManagement:
    """Test Inning management endpoints"""
    
    def setup_method(self):
        """Clear database before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def _create_match(self):
        """Helper to create a match"""
        payload = {
            "team1_name": "Team A",
            "team2_name": "Team B",
            "striker_batsman": "Batsman1",
            "non_striker_batsman": "Batsman2",
            "striker_bowler": "Bowler1"
        }
        response = client.post("/matches/quickmatches/", json=payload)
        return response.json()["match_id"]
    
    def test_start_inning_success(self):
        """Test starting an inning"""
        match_id = self._create_match()
        
        response = client.post(
            f"/matches/quickmatches/{match_id}/start-inning",
            params={
                "striker_batsman": "MainBatsman1",
                "non_striker_batsman": "MainBatsman2",
                "striker_bowler": "MainBowler1"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully" in data["message"].lower()
        assert data["match_id"] == match_id
    
    def test_start_inning_nonexistent_match(self):
        """Test starting inning for non-existent match"""
        response = client.post(
            "/matches/quickmatches/9999/start-inning",
            params={
                "striker_batsman": "Batsman1",
                "non_striker_batsman": "Batsman2",
                "striker_bowler": "Bowler1"
            }
        )
        assert response.status_code == 404
    
    def test_add_ball_success(self):
        """Test adding a ball"""
        match_id = self._create_match()
        
        # Start inning first
        client.post(
            f"/matches/quickmatches/{match_id}/start-inning",
            params={
                "striker_batsman": "Batsman1",
                "non_striker_batsman": "Batsman2",
                "striker_bowler": "Bowler1"
            }
        )
        
        # Add ball
        ball_data = {
            "run_scored": 4,
            "is_wide_ball": False,
            "is_out": False
        }
        response = client.post(
            f"/matches/quickmatches/{match_id}/add-ball",
            json=ball_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "ball_id" in data
    
    def test_end_inning_success(self):
        """Test ending an inning"""
        match_id = self._create_match()
        
        # Start inning
        client.post(
            f"/matches/quickmatches/{match_id}/start-inning",
            params={
                "striker_batsman": "Batsman1",
                "non_striker_batsman": "Batsman2",
                "striker_bowler": "Bowler1"
            }
        )
        
        # End inning
        response = client.post(f"/matches/quickmatches/{match_id}/end-inning")
        assert response.status_code == 200
        data = response.json()
        assert "successfully" in data["message"].lower()


class TestDataValidation:
    """Test data validation and edge cases"""
    
    def setup_method(self):
        """Clear database before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_create_match_with_special_characters(self):
        """Test creating match with special characters in team names"""
        payload = {
            "team1_name": "Team A & B!",
            "team2_name": "Team C/D",
            "striker_batsman": "Player@1",
            "non_striker_batsman": "Player#2",
            "striker_bowler": "Bowler$1"
        }
        
        response = client.post("/matches/quickmatches/", json=payload)
        assert response.status_code == 201
    
    def test_create_match_with_empty_optional_fields(self):
        """Test creating match with empty optional fields"""
        payload = {
            "team1_name": "Team A",
            "team2_name": "Team B",
            "striker_batsman": None,
            "non_striker_batsman": None,
            "striker_bowler": None
        }
        
        response = client.post("/matches/quickmatches/", json=payload)
        assert response.status_code == 201
    
    def test_match_data_persistence(self):
        """Test that match data persists correctly"""
        payload = {
            "team1_name": "Persistent Team 1",
            "team1_image": "https://example.com/persistent1.jpg",
            "team2_name": "Persistent Team 2",
            "team2_image": "https://example.com/persistent2.jpg",
            "striker_batsman": "PersistentBatsman1",
            "non_striker_batsman": "PersistentBatsman2",
            "striker_bowler": "PersistentBowler1",
            "match_settings": {"overs": 20, "format": "T20"},
            "toss_info": {"winner": "team1", "decision": "bat"}
        }
        
        # Create
        create_response = client.post("/matches/quickmatches/", json=payload)
        match_id = create_response.json()["match_id"]
        
        # Retrieve and verify
        get_response = client.get(f"/matches/quickmatches/{match_id}")
        data = get_response.json()
        assert data["team1_name"] == "Persistent Team 1"
        assert data["team2_name"] == "Persistent Team 2"
        assert data["striker_batsman"] == "PersistentBatsman1"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Clear database before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/matches/quickmatches/",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_batch_operations(self):
        """Test creating multiple matches"""
        for i in range(5):
            payload = {
                "team1_name": f"Team {i}A",
                "team2_name": f"Team {i}B",
                "striker_batsman": f"Batsman{i}1",
                "non_striker_batsman": f"Batsman{i}2",
                "striker_bowler": f"Bowler{i}1"
            }
            response = client.post("/matches/quickmatches/", json=payload)
            assert response.status_code == 201
        
        # Verify all were created
        response = client.get("/matches/quickmatchs/")
        assert response.json()["count"] == 5


# Run tests with: pytest test_api.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
