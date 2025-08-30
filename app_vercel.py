#!/usr/bin/env python3
"""
Vercel-compatible version of the polling app.
This version removes WebSocket dependencies and uses polling for updates.
"""

from flask import Flask, request, render_template, redirect, url_for, jsonify, make_response, send_file
import sqlite3, datetime, qrcode, io, uuid, os, hashlib, tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Use temporary directory for database in serverless environment
DB_PATH = os.path.join(tempfile.gettempdir(), "poll.db")

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    c = db.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS polls (
                    id INTEGER PRIMARY KEY,
                    question TEXT NOT NULL,
                    expiry TEXT NOT NULL,
                    hide_results INTEGER DEFAULT 0,
                    creator_secret TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    insights_generated INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS options (
                    id INTEGER PRIMARY KEY,
                    poll_id INTEGER NOT NULL,
                    text TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY,
                    poll_id INTEGER NOT NULL,
                    option_id INTEGER NOT NULL,
                    vote_token TEXT,
                    device_hash TEXT,
                    ip TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY,
                    poll_id INTEGER NOT NULL,
                    insight_text TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )''')
    
    db.commit()
    db.close()

# Initialize database on import
init_db()

# Utils (same as original)
def auto_split_options(question: str):
    delimiters = ['|', ';', ' vs ', ' VS ', ' or ', ' OR ']
    for d in delimiters:
        if d in question:
            parts = [p.strip() for p in question.split(d) if p.strip()]
            if 2 <= len(parts) <= 4:
                return parts
    return None

def generate_vote_token():
    return str(uuid.uuid4())

def generate_creator_secret():
    return str(uuid.uuid4())

def get_device_hash(request):
    ua = request.headers.get('User-Agent', '')
    ip = request.remote_addr or ''
    return hashlib.md5(f"{ua}:{ip}".encode()).hexdigest()

def generate_insights(poll_id, results, total_votes):
    if total_votes < 20:
        return None
    
    winner = max(results, key=lambda x: x[1])
    winner_text, winner_count, _, winner_pct = winner
    
    insights = []
    
    if winner_pct > 60:
        insights.append(f"Clear winner: '{winner_text}' dominates with {winner_pct}% of votes")
    elif winner_pct < 35:
        insights.append(f"Close race: No clear consensus, '{winner_text}' leads narrowly at {winner_pct}%")
    else:
        insights.append(f"Moderate lead: '{winner_text}' has a solid lead with {winner_pct}% of votes")
    
    if total_votes >= 50:
        insights.append(f"High engagement: {total_votes} participants shows strong interest")
    elif total_votes >= 30:
        insights.append(f"Good participation: {total_votes} votes collected")
    
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    if len(sorted_results) >= 2:
        gap = sorted_results[0][3] - sorted_results[1][3]
        if gap < 10:
            insights.append("Very competitive: Top options are neck-and-neck")
        elif gap > 30:
            insights.append("Decisive outcome: Clear preference established")
    
    return " • ".join(insights)

def poll_results(poll_id: int):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, text FROM options WHERE poll_id=?", (poll_id,))
    options = c.fetchall()
    results = []
    total = 0
    for row in options:
        c.execute("SELECT COUNT(*) FROM votes WHERE option_id=?", (row['id'],))
        cnt = c.fetchone()[0]
        total += cnt
        results.append((row['text'], cnt, row['id']))
    
    if total > 0:
        results = [(t, c, oid, round(c * 100.0 / total, 1)) for (t, c, oid) in results]
    else:
        results = [(t, c, oid, 0.0) for (t, c, oid) in results]
    
    db.close()
    return results, total

# Routes (same as original but without WebSocket)
@app.route("/", methods=["GET", "POST"])
def create_poll():
    if request.method == "POST":
        question = request.form["question"].strip()
        hide_results = 1 if request.form.get("hide_results") else 0

        auto = auto_split_options(question)
        if auto:
            options = auto
        else:
            try:
                n = int(request.form.get("num_options", "2"))
            except ValueError:
                n = 2
            n = max(2, min(4, n))
            options = []
            for i in range(1, n + 1):
                val = (request.form.get(f"option{i}") or "").strip()
                if val:
                    options.append(val)

        if not (2 <= len(options) <= 4):
            return "Provide 2 to 4 options.", 400
        if len(question) == 0 or len(question) > 120:
            return "Question is required (1–120 chars).", 400

        expiry = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
        creator_secret = generate_creator_secret()
        
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO polls (question, expiry, hide_results, creator_secret) VALUES (?, ?, ?, ?)", 
                  (question, expiry, hide_results, creator_secret))
        poll_id = c.lastrowid
        for opt in options:
            c.execute("INSERT INTO options (poll_id, text) VALUES (?, ?)", (poll_id, opt))
        db.commit()
        db.close()
        return redirect(url_for("share_poll", poll_id=poll_id, secret=creator_secret))

    return render_template("create.html")

@app.route("/poll/<int:poll_id>", methods=["GET", "POST"])
def poll_view(poll_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT question, expiry, hide_results FROM polls WHERE id=?", (poll_id,))
    row = c.fetchone()
    if not row:
        db.close()
        return "Poll not found", 404

    question, expiry, hide = row["question"], row["expiry"], bool(row["hide_results"])
    expiry_dt = datetime.datetime.fromisoformat(expiry)
    expired = datetime.datetime.now() > expiry_dt
    if expired:
        db.close()
        return redirect(url_for("results_view", poll_id=poll_id))

    vote_token = request.cookies.get("vote_token")
    has_voted = False
    user_choice = None
    if vote_token:
        c.execute("SELECT option_id FROM votes WHERE poll_id=? AND vote_token=?", (poll_id, vote_token))
        r = c.fetchone()
        if r:
            has_voted = True
            user_choice = r[0]

    if request.method == "POST" and not has_voted:
        option_id = request.form.get("option")
        if not option_id:
            db.close()
            return "No option selected.", 400
        c.execute("SELECT 1 FROM options WHERE id=? AND poll_id=?", (option_id, poll_id))
        if not c.fetchone():
            db.close()
            return "Invalid option.", 400

        new_token = generate_vote_token()
        c.execute("INSERT INTO votes (poll_id, option_id, vote_token, device_hash, ip) VALUES (?, ?, ?, ?, ?)",
                  (poll_id, option_id, new_token, get_device_hash(request), request.remote_addr))
        
        # Check for insights
        c.execute("SELECT COUNT(*) FROM votes WHERE poll_id=?", (poll_id,))
        total_after_vote = c.fetchone()[0]
        
        if total_after_vote >= 20:
            c.execute("SELECT insights_generated FROM polls WHERE id=?", (poll_id,))
            row = c.fetchone()
            insights_generated = row[0] if row else 0
            if not insights_generated:
                results, total = poll_results(poll_id)
                insight_text = generate_insights(poll_id, results, total)
                if insight_text:
                    c.execute("INSERT INTO insights (poll_id, insight_text) VALUES (?, ?)", (poll_id, insight_text))
                    c.execute("UPDATE polls SET insights_generated=1 WHERE id=?", (poll_id,))
        
        db.commit()
        db.close()
        
        resp = make_response(redirect(url_for("results_view", poll_id=poll_id)))
        resp.set_cookie("vote_token", new_token, max_age=86400, httponly=True, samesite="Strict")
        return resp

    c.execute("SELECT id, text FROM options WHERE poll_id=?", (poll_id,))
    options = c.fetchall()
    results, total = ([], 0)
    if not hide:
        results, total = poll_results(poll_id)

    # Get options text for OG description
    c.execute("SELECT text FROM options WHERE poll_id=? ORDER BY id LIMIT 4", (poll_id,))
    option_texts = [row[0] for row in c.fetchall()]
    og_description = f"Vote on: {' vs '.join(option_texts[:2])}" + (f" and {len(option_texts)-2} more" if len(option_texts) > 2 else "")

    db.close()
    return render_template("poll_vercel.html",
                           poll_id=poll_id,
                           question=question,
                           options=options,
                           has_voted=has_voted,
                           user_choice=user_choice,
                           hide_results=hide,
                           results=results,
                           total_votes=total,
                           og_description=og_description)

@app.route("/results/<int:poll_id>")
def results_view(poll_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT question, expiry, hide_results FROM polls WHERE id=?", (poll_id,))
    row = c.fetchone()
    if not row:
        db.close()
        return "Poll not found", 404
    
    question, expiry, _ = row["question"], row["expiry"], row["hide_results"]
    expiry_dt = datetime.datetime.fromisoformat(expiry)
    expired = datetime.datetime.now() > expiry_dt

    results, total = poll_results(poll_id)

    vote_token = request.cookies.get("vote_token")
    has_voted = False
    user_choice = None
    if vote_token:
        c.execute("SELECT option_id FROM votes WHERE poll_id=? AND vote_token=?", (poll_id, vote_token))
        r = c.fetchone()
        if r:
            has_voted = True
            user_choice = r[0]

    # Get insights if available
    c.execute("SELECT insight_text FROM insights WHERE poll_id=? ORDER BY created_at DESC LIMIT 1", (poll_id,))
    insight_row = c.fetchone()
    insights = insight_row[0] if insight_row else None

    db.close()
    return render_template("results.html",
                           poll_id=poll_id,
                           question=question,
                           results=results,
                           total=total,
                           has_voted=has_voted,
                           user_choice=user_choice,
                           is_expired=expired,
                           insights=insights)

@app.route("/api/results/<int:poll_id>")
def api_results(poll_id):
    results, total = poll_results(poll_id)
    return jsonify({
        "results": [{"text": t, "count": c, "percentage": p} for (t, c, oid, p) in results],
        "total_votes": total
    })

@app.route("/share/<int:poll_id>")
def share_poll(poll_id):
    secret = request.args.get('secret')
    db = get_db()
    c = db.cursor()
    c.execute("SELECT question, creator_secret FROM polls WHERE id=?", (poll_id,))
    row = c.fetchone()
    if not row:
        db.close()
        return "Poll not found", 404
    
    creator_secret = row["creator_secret"]
    is_creator = secret and creator_secret and secret == creator_secret
    link = url_for("poll_view", poll_id=poll_id, _external=True)
    creator_link = url_for("creator_dashboard", poll_id=poll_id, secret=creator_secret, _external=True) if is_creator and creator_secret else None
    
    db.close()
    return render_template("share.html", 
                         link=link, 
                         poll_id=poll_id, 
                         question=row["question"],
                         creator_link=creator_link,
                         is_creator=is_creator)

@app.route("/creator/<int:poll_id>/<secret>")
def creator_dashboard(poll_id, secret):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT question, expiry, hide_results, creator_secret, created_at FROM polls WHERE id=?", (poll_id,))
    row = c.fetchone()
    if not row or not row["creator_secret"] or row["creator_secret"] != secret:
        db.close()
        return "Access denied", 403
    
    question, expiry, hide_results, _, created_at = row["question"], row["expiry"], row["hide_results"], row["creator_secret"], row["created_at"]
    expiry_dt = datetime.datetime.fromisoformat(expiry)
    created_dt = datetime.datetime.fromisoformat(created_at) if created_at else datetime.datetime.now()
    expired = datetime.datetime.now() > expiry_dt
    
    results, total = poll_results(poll_id)
    
    # Get insights if available
    c.execute("SELECT insight_text, created_at FROM insights WHERE poll_id=? ORDER BY created_at DESC LIMIT 1", (poll_id,))
    insight_row = c.fetchone()
    insights = insight_row["insight_text"] if insight_row else None
    
    # Get vote timeline
    c.execute("""SELECT DATE(created_at) as vote_date, COUNT(*) as count 
                 FROM votes WHERE poll_id=? 
                 GROUP BY DATE(created_at) 
                 ORDER BY vote_date DESC LIMIT 7""", (poll_id,))
    timeline = c.fetchall()
    
    poll_link = url_for("poll_view", poll_id=poll_id, _external=True)
    
    db.close()
    return render_template("creator_dashboard.html",
                         poll_id=poll_id,
                         question=question,
                         results=results,
                         total=total,
                         insights=insights,
                         timeline=timeline,
                         poll_link=poll_link,
                         created_at=created_dt,
                         expiry_dt=expiry_dt,
                         is_expired=expired)

@app.route("/qr/<int:poll_id>")
def qr_code(poll_id):
    link = url_for("poll_view", poll_id=poll_id, _external=True)
    img = qrcode.make(link)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return app.response_class(buf.getvalue(), mimetype="image/png")

# Vercel entry point
app = app