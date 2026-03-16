import json
import requests
r = requests.post('http://127.0.0.1:8000/matches/quickmatches/' , data=json.dumps({
    "team1_name": "string",
        "team1_image": None,
        "team2_name": "string",
        "team2_image": None,
        "match_settings": {
            "additionalProp1": {}
        },
        "toss_info": {
            "additionalProp1": {}
        },
        "striker_batsman": "string",
        "non_striker_batsman": "string",
        "striker_bowler": "string",
        "non_striker_bowler": "string",
        "team_name": "string"
}))

print(r.text)