# CrickStars UI Design Guide

## 📋 Overview

The CrickStars application now features a professional, Postman collection-compatible cricket match management UI based on your `crikstar` design system. The interface is fully responsive, modern, and integrated with your FastAPI backend.

---

## 🎨 Design System

### Colors
- **Primary**: `#3B43F2` (Deep Blue) - Main CTA buttons, branding
- **Secondary**: `#2EA850` (Green) - Positive actions, scores
- **Live Badge**: `#FF4545` (Red) - Live indicator with pulse animation
- **Background**: `#FAFAFA` (Light Gray) - Page background
- **Text Primary**: `#030311` (Dark) - Main content
- **Text Secondary**: `#666` (Gray) - Supporting text
- **Border**: `#ECECEE` (Light Gray) - Dividers, tab containers

### Typography
- **Font**: Montserrat (Google Fonts)
- **Weights**: 400 (Regular), 600 (Semi-bold), 700 (Bold)
- **Sizes**: 
  - H1: 28px (Desktop), 24px (Mobile)
  - H2: 18px-20px
  - Body: 14px-16px
  - Small: 12px-13px

### Spacing
- **Container Max-Width**: 1440px (Desktop)
- **Padding**: 20px (Mobile), 60px (Tablet), 100px (Desktop)
- **Gap**: 8px (small), 12px (medium), 20px (large)

---

## 📄 Pages & Routes

### 1. **Dashboard** (`GET /`)
**File**: `templates/index.html`

Main entry point for match management with 3 tabs:

#### Tab 1: Summary
- Create new match form
  - Team 1 & 2 names and logos
  - Initial striker, non-striker, bowler
  - Submit button creates match with auto-generated ID
- Load match card
  - Match ID input with load button
  - List of recent matches (clickable to select)
  - Delete selected match button

#### Tab 2: Scorecard
- Displays match scorecard when loaded
- Shows overs and ball details

#### Tab 3: Controls
- **Add Ball/Score**
  - Runs scored input
  - Checkboxes: Wide, No Ball, Bye, Leg Bye, Out
  - Out type text input
  - Submit button
- **Match Controls**
  - Swap Batsman
  - Swap Bowler
  - End Inning
  - Start 2nd Inning

### 2. **Live Match** (`GET /live.html`)
**File**: `templates/live.html`

Real-time match tracking with:
- Live badge with pulsing animation
- Team vs Team display
- 3 tabs: Overs | Scorecard | Commentary
- Quick stats sidebar (Total balls, sixes, fours, wickets)
- Auto-refresh every 5 seconds

---

## 🔧 Components

### Match Card
```html
<div class="card">
  <!-- Team logos, scores, overs -->
  <!-- Match metadata (striker, bowler) -->
</div>
```

### Ball Display
```html
<div class="ball ball-dot">.</div>      <!-- Dot ball -->
<div class="ball ball-run">1</div>      <!-- Run -->
<div class="ball ball-boundary">4</div> <!-- Boundary -->
<div class="ball ball-six">6</div>      <!-- Six -->
<div class="ball ball-wicket">W</div>   <!-- Wicket -->
```

### Tab Container
```html
<div class="tab-container">
  <button class="tab-btn active">Summary</button>
  <button class="tab-btn">Scorecard</button>
  <button class="tab-btn">Controls</button>
</div>
```

### Forms
All form inputs use:
- Light background: `#f0f0f0` (focus: `#3B43F2`)
- Border radius: 10px
- Full width responsive

---

## 🎯 API Integration

### Create Match
```javascript
POST /matches/quickmatches/
{
  "team1_name": "Team 1",
  "team1_image": "https://...",
  "team2_name": "Team 2",
  "team2_image": "https://...",
  "striker_batsman": "Player 1",
  "non_striker_batsman": "Player 2",
  "striker_bowler": "Bowler 1",
  "team_name": "Team 1",
  "match_settings": {},
  "toss_info": {"toss_winner_team_name": "Team 1", "choose_to": "bat"}
}
```

### Load Match
```javascript
GET /matches/quickmatches/{match_id}
```

### Add Score
```javascript
POST /matches/quickmatches/{match_id}/add-score
{
  "runs": 1,
  "is_wide": 0,
  "is_no_ball": 0,
  "is_bye": 0,
  "is_leg_bye": 0,
  "is_out": 0,
  "out_type": "",
  "team_name": "Team 1"
}
```

### Match Controls
```javascript
POST /matches/quickmatches/{match_id}/swap-batsman
POST /matches/quickmatches/{match_id}/swap-bowler
POST /matches/quickmatches/{match_id}/end-inning
POST /matches/quickmatches/{match_id}/start-second-inning
```

### Legacy Endpoints (Postman-Compatible)
```
/create-match
/list-match
/update-match
/delete-match
/start-match
/add-score
/get-score
/swap-batsman
/swap-bowler
/end-inning
```

---

## 📱 Responsive Design

### Mobile (< 768px)
- Single column layout
- Compact spacing (20px padding)
- Smaller fonts and buttons
- Stacked team displays

### Tablet (768px - 1024px)
- Grid layout (2 columns)
- Medium spacing (60px padding)
- 1/2 width for forms/cards

### Desktop (> 1024px)
- Full-width grid layout
- Sidebar for quick stats (live.html)
- 100px padding
- 3-column layout where applicable

---

## ✨ Animations

### Live Badge
```css
animation: zoom 1s ease-in-out infinite;
```
Pulses every 1 second for "LIVE" indicator

### Tab Transition
```css
transition: all 0.3s ease;
```
Smooth color/background changes on switching tabs

### Button Hover
```css
transform: translateY(-2px);
box-shadow: 0 4px 12px rgba(59, 67, 242, 0.3);
```
Lifts button up with blue glow on hover

---

## 🚀 How to Run

```bash
cd c:\Users\dimpa\Desktop\NewFolder\CrickStars

# Activate venv
venv\Scripts\Activate.ps1

# Start server
python -m uvicorn main:app --reload

# Open in browser
# http://127.0.0.1:8000/
```

---

## 📋 File Structure

```
templates/
  ├── index.html         (Dashboard - Main page)
  ├── live.html          (Live match tracker)
  └── base.html          (Legacy backup)

static/
  ├── css/
  │   └── style.css      (Custom CSS if needed)
  └── img/               (Match images, logos, etc)

routers/
  └── create_match_route.py  (All API endpoints)
```

---

## 🎯 User Journey

1. **User opens `http://127.0.0.1:8000/`**
   - Dashboard loads with Summary tab active

2. **Create Match**
   - Fill form (team names, logos, players)
   - Click "Create Match"
   - Gets auto-generated Match ID

3. **Load/View Match**
   - Enter Match ID or click recent match
   - UI displays team info, current status
   - Switch to Controls tab

4. **Add Scores**
   - Select runs, extras, wickets
   - Click "Add Score"
   - UI refreshes with new data

5. **Live Tracking** (Optional)
   - Click match from dashboard
   - Opens live.html with real-time updates
   - Auto-refreshes every 5 seconds

---

## 🎨 Customization

### Change Primary Color
Find `.btn-primary` in CSS and change `background-color: #3B43F2` to your color

### Add Custom Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

### Add Team Logos
Upload to `static/img/` and reference in create form

### Extend Scorecard
Modify `loadScorecard()` function in `index.html` to display more data

---

## ✅ Testing

All endpoints tested and passing (21/21 tests):

```bash
python -m pytest -q
```

This validates:
- CRUD operations
- Score calculations
- Inning management
- Data validation
- API response formats

---

## 📞 Support

For issues or questions:
1. Check browser console (F12)
2. Review API responses in Network tab
3. Verify match ID is correct
4. Ensure backend is running (`uvicorn`)
5. Check test suite: `pytest`

---

## 🔐 Notes

- All data stored in SQLite (test) / MySQL (production)
- Match IDs are auto-generated integers
- Times are in UTC (SQLAlchemy default)
- CORS enabled for cross-origin requests
- All endpoints require valid JSON payloads
- No authentication currently (add if needed)

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Built with**: FastAPI + Tailwind CSS + Vanilla JS
