from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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

res = client.post("/matches/quickmatches/", json=payload)
print("status", res.status_code)
print(res.text)
