# 🏏 CrickStars Quick Start Guide

## ✅ What You Got

A **production-ready cricket match management UI** with:

- ✨ **Professional Dashboard** - Create, manage, and score matches
- 🎨 **Modern Design** - Based on your `crikstar` design system (Montserrat font, blue/green/red colors)
- 📱 **Fully Responsive** - Mobile, tablet, desktop layouts
- ⚡ **Real-time Updates** - Live match tracking with auto-refresh
- 🔗 **API Integrated** - All endpoints connected and tested
- ✅ **All Tests Passing** - 21/21 unit tests pass

---

## 🚀 Get Started (Fast!)

### Step 1: Start the server
```bash
cd c:\Users\dimpa\Desktop\NewFolder\CrickStars
venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

### Step 2: Open in browser
```
http://127.0.0.1:8000/
```

### Step 3: Create a match
1. Fill in the **Create Quick Match** form:
   - Team 1 name: `Mumbai Strikers`
   - Team 1 logo: (any image URL or leave blank)
   - Team 2 name: `Delhi Capitals`
   - Team 2 logo: (any image URL or leave blank)
   - Striker: `Virat Kohli`
   - Non-Striker: `Rishabh Pant`
   - Bowler: `Jasprit Bumrah`

2. Click **Create Match** → You get a Match ID ✅

### Step 4: Add scores
1. Switch to **Controls** tab
2. Enter runs (e.g., `1`)
3. Check **Wide**, **Bye**, or **Out** if applicable
4. Click **Add Score** → Score updated! ✅

### Step 5: View live
1. Go to `/live?id=YOUR_MATCH_ID` to see real-time dashboard
2. Auto-refreshes every 5 seconds

---

## 📍 Endpoints Overview

| Action | Route | Method |
|--------|-------|--------|
| Create Match | `/matches/quickmatches/` | POST |
| Load Match | `/matches/quickmatches/{id}` | GET |
| Delete Match | `/matches/quickmatchs/{id}` | DELETE |
| Add Score | `/matches/quickmatches/{id}/add-score` | POST |
| Swap Batsman | `/matches/quickmatches/{id}/swap-batsman` | POST |
| Swap Bowler | `/matches/quickmatches/{id}/swap-bowler` | POST |
| End Inning | `/matches/quickmatches/{id}/end-inning` | POST |
| Start 2nd Inning | `/matches/quickmatches/{id}/start-second-inning` | POST |
| Get Score | `/matches/quickmatches/{id}/score` | GET |

**Legacy Postman-style:**
```
POST /create-match
POST /list-match
POST /update-match
POST /delete-match
POST /start-match
POST /add-score
POST /get-score
POST /swap-batsman
POST /swap-bowler
POST /end-inning
```

---

## 🎨 Design Highlights

### Colors
- **Primary Blue**: `#3B43F2` - Buttons, branding
- **Success Green**: `#2EA850` - Scores, positive actions
- **Live Red**: `#FF4545` - Live indicator (animated)

### Pages
1. **Dashboard** (`/`) - Create & manage matches
2. **Live View** (`/live?id=X`) - Real-time tracking
3. **Match Detail** (`/match/{id}`) - Detailed scorecard

### Responsive
- **Mobile** (320px+): Stacked layout, compact spacing
- **Tablet** (768px+): 2-column grid
- **Desktop** (1200px+): 3-column with sidebar

---

## 📂 File Structure

```
CrickStars/
├── templates/
│   ├── index.html          ← Main dashboard
│   └── live.html           ← Live view
├── routers/
│   └── create_match_route.py  ← All APIs
├── services/
│   ├── add_score_services.py  ← Score logic
│   └── inning_services.py     ← Inning logic
├── db/
│   ├── model.py            ← Database models
│   └── database.py         ← DB config
├── static/
│   └── css/                ← Custom styles
├── main.py                 ← Server entry
├── test_api.py             ← Tests (21 passing)
└── DESIGN_GUIDE.md         ← Full design docs
```

---

## 🧪 Run Tests

```bash
# All tests
python -m pytest -q

# Specific test
python -m pytest test_api.py::TestQuickMatchCRUD::test_create_match_success -v

# With output
python -m pytest --tb=short
```

**Status**: ✅ 21/21 tests passing

---

## 🎯 Common Tasks

### Create a match from code
```python
import requests

data = {
    "team1_name": "Team A",
    "team2_name": "Team B",
    "striker_batsman": "Player 1",
    "non_striker_batsman": "Player 2",
    "striker_bowler": "Bowler 1"
}

res = requests.post("http://127.0.0.1:8000/matches/quickmatches/", json=data)
match_id = res.json()["match_id"]
print(f"Created match {match_id}")
```

### Add a score from code
```python
score_data = {
    "runs": 4,
    "is_wide": 0,
    "is_no_ball": 0,
    "is_out": 0,
    "team_name": "Team A"
}

res = requests.post(f"http://127.0.0.1:8000/matches/quickmatches/{match_id}/add-score", json=score_data)
print(res.json())
```

### Get match score
```python
res = requests.get(f"http://127.0.0.1:8000/matches/quickmatches/{match_id}/score")
print(res.json())
```

---

## 🛠️ Customization

### Change colors
Edit `index.html` `<style>` section:
```css
--primary-color: #3B43F2;  /* Change primary blue */
```

### Add more fields to match form
In `index.html`, add inputs to create form and update POST payload

### Change refresh interval
In `live.html`, modify:
```javascript
setInterval(loadScore, 5000);  // 5000ms = 5 seconds
```

### Add authentication
Add FastAPI dependency in `routers/create_match_route.py`

---

## ❓ FAQ

**Q: Players not saving?**  
A: Make sure Players table exists. Check `db/model.py` - it's enabled.

**Q: API returning 404?**  
A: Match ID might not exist. Use the "All Matches" list to find correct ID.

**Q: Scores not updating?**  
A: Refresh page or switch tabs to trigger UI update.

**Q: What's the database?**  
A: SQLite for development, MySQL for production (config in `db/database.py`).

**Q: Can I delete a match?**  
A: Yes! Controls tab > "Delete Selected Match" button.

**Q: How do I view scorecard details?**  
A: Switch to **Scorecard** tab on main dashboard or view `/live?id=MATCH_ID`.

---

## 📊 Architecture

```
User Browser
    ↓
Jinja2 HTML Templates (index.html, live.html)
    ↓
Vanilla JS Fetch API
    ↓
FastAPI Router (create_match_route.py)
    ↓
SQLAlchemy ORM Models (db/model.py)
    ↓
SQLite / MySQL Database
```

---

## 🔗 Used Technologies

- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML5 + Vanilla JS (no frameworks)
- **CSS**: Tailwind CSS + custom styles
- **Database**: SQLAlchemy + SQLite/MySQL
- **Testing**: pytest
- **Font**: Montserrat (Google Fonts)

---

## 📝 Next Steps (Optional)

1. **Deploy**: Use Gunicorn + Nginx or Railway/Heroku
2. **Add Auth**: JWT tokens for user sessions
3. **Add Players**: Manage player profiles and stats
4. **Add Teams**: Create team management module
5. **Add Leagues**: Support tournament structures
6. **Add Notifications**: Webhook alerts for match events
7. **Add Analytics**: Match stats and player performance
8. **Add Mobile App**: React Native / Flutter wrapper

---

## 💡 Tips

- Copy match URL to share: `http://127.0.0.1:8000/live?id=123`
- Use browser DevTools (F12) to debug network requests
- Check server logs for detailed error messages
- Run `pytest -vv` for verbose test output with timings
- Save frequently used match IDs for quick loading

---

## 🆘 Need Help?

1. Check `DESIGN_GUIDE.md` for detailed API docs
2. Review `test_api.py` for usage examples
3. Check browser console (`F12 → Console`) for JS errors
4. Run `python -m pytest --tb=long` for detailed test output
5. Check `main.py` logs for server errors

---

**You're all set!** Start creating and scoring matches! 🏏⚡

Created: March 2026  
Version: 1.0  
Built with ❤️ by CrickStars Team
