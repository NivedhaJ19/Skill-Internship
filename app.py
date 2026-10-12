import os
import sqlite3
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, query_db, execute_db, init_db
from ai_service import get_ai_career_advice, extract_skills_from_text

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smart_internship_platform_secret_key_2026")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------------------------------------------------
# Context Processor & Auth Decorators
# -------------------------------------------------------------

@app.context_processor
def inject_user_and_roles():
    current_user = None
    if 'user_id' in session:
        current_user = query_db(
            "SELECT id, name, email, role, target_role, headline FROM users WHERE id = ?",
            [session['user_id']], one=True
        )
    roles = query_db("SELECT id, title, category, icon FROM job_roles ORDER BY title ASC")
    return {
        'current_user': current_user,
        'all_roles': roles
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in as administrator.", "warning")
            return redirect(url_for('login'))
        user = query_db("SELECT role FROM users WHERE id = ?", [session['user_id']], one=True)
        if not user or user['role'] != 'admin':
            flash("Administrator privileges required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------

def calculate_readiness(user_skills_dict, role_id_or_title):
    """
    Calculates weighted skill gap and readiness score against role benchmark.
    Returns { readiness, matched, improve, missing, radar_data, total_weight }
    """
    if isinstance(role_id_or_title, int):
        role_skills = query_db(
            "SELECT skill_name, required_level, weight, category FROM role_skills WHERE role_id = ?",
            [role_id_or_title]
        )
    else:
        role = query_db("SELECT id FROM job_roles WHERE title = ?", [role_id_or_title], one=True)
        if not role:
            return None
        role_skills = query_db(
            "SELECT skill_name, required_level, weight, category FROM role_skills WHERE role_id = ?",
            [role['id']]
        )

    matched, improve, missing = [], [], []
    weighted_score = 0
    total_weight = 0

    radar_labels = []
    user_levels = []
    required_levels = []

    for item in role_skills:
        skill = item['skill_name']
        required = item['required_level']
        weight = item['weight']
        category = item['category']
        current = user_skills_dict.get(skill, 0)

        total_weight += weight
        weighted_score += weight * min(current / required, 1.0)

        skill_info = {
            "name": skill,
            "required": required,
            "current": current,
            "weight": weight,
            "category": category,
            "gap": max(0, required - current)
        }

        radar_labels.append(skill)
        user_levels.append(current)
        required_levels.append(required)

        if current >= required:
            matched.append(skill_info)
        elif current > 0:
            improve.append(skill_info)
        else:
            missing.append(skill_info)

    readiness = round((weighted_score / total_weight) * 100) if total_weight > 0 else 0

    return {
        "readiness": readiness,
        "matched": matched,
        "improve": improve,
        "missing": missing,
        "radar": {
            "labels": radar_labels,
            "user_data": user_levels,
            "target_data": required_levels
        }
    }

# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db("SELECT * FROM users WHERE LOWER(email) = ?", [email], one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('admin' if user['role'] == 'admin' else 'dashboard'))
        else:
            flash("Invalid email or password. Use demo credentials or register.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        target_role = request.form.get('target_role', 'Full-Stack Developer')
        education = request.form.get('education', '').strip()
        institution = request.form.get('institution', '').strip()

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('register.html')

        existing = query_db("SELECT id FROM users WHERE LOWER(email) = ?", [email], one=True)
        if existing:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        p_hash = generate_password_hash(password)
        headline = f"Aspiring {target_role}"
        
        user_id = execute_db("""
            INSERT INTO users (name, email, password_hash, role, headline, education, institution, target_role)
            VALUES (?, ?, ?, 'student', ?, ?, ?, ?)
        """, [name, email, p_hash, headline, education, institution, target_role])

        # Automatically seed a milestone for the new student
        execute_db("""
            INSERT INTO skill_milestones (user_id, skill_name, milestone_title, completed)
            VALUES (?, 'Orientation', 'Complete initial skill self-assessment and set target role', 1)
        """, [user_id])

        # Award Welcome Badge
        execute_db("""
            INSERT INTO user_badges (user_id, badge_name, badge_icon, description)
            VALUES (?, 'Platform Explorer', 'sparkles', 'Joined SkillBridge and established your career learning trajectory.')
        """, [user_id])

        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = 'student'
        flash("Registration successful! Welcome to SkillBridge.", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------------
# Public Landing Page & Interactive Preview
# -------------------------------------------------------------

@app.route('/')
def index():
    roles = query_db("SELECT * FROM job_roles ORDER BY id ASC")
    internships = query_db("SELECT * FROM internships ORDER BY id ASC LIMIT 6")
    stats = {
        "roles_count": len(roles),
        "internships_count": query_db("SELECT COUNT(*) as c FROM internships", one=True)['c'],
        "resources_count": query_db("SELECT COUNT(*) as c FROM learning_resources", one=True)['c'],
        "students_count": query_db("SELECT COUNT(*) as c FROM users WHERE role = 'student'", one=True)['c']
    }
    return render_template('index.html', roles=roles, internships=internships, stats=stats)

# -------------------------------------------------------------
# Student Dashboard & Profile
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    target_role_title = user['target_role'] or 'Full-Stack Developer'
    target_role = query_db("SELECT * FROM job_roles WHERE title = ?", [target_role_title], one=True)
    if not target_role:
        target_role = query_db("SELECT * FROM job_roles LIMIT 1", one=True)
        target_role_title = target_role['title']

    # Retrieve user's skills
    user_skills_raw = query_db("SELECT * FROM user_skills WHERE user_id = ? ORDER BY skill_name ASC", [session['user_id']])
    user_skills_dict = {row['skill_name']: row['proficiency_level'] for row in user_skills_raw}

    # Analyze readiness
    analysis = calculate_readiness(user_skills_dict, target_role['id'])

    # Retrieve user's projects
    projects = query_db("SELECT * FROM user_projects WHERE user_id = ? ORDER BY created_at DESC", [session['user_id']])

    # Retrieve badges
    badges = query_db("SELECT * FROM user_badges WHERE user_id = ? ORDER BY earned_at DESC", [session['user_id']])

    # Retrieve milestones
    milestones = query_db("SELECT * FROM skill_milestones WHERE user_id = ? ORDER BY completed ASC, id DESC", [session['user_id']])

    # Retrieve recommended internships
    all_role_internships = query_db("SELECT * FROM internships WHERE role_title = ?", [target_role_title])
    recommended = []
    for item in all_role_internships:
        req_skills = [s.strip() for s in item['required_skills'].split(',') if s.strip()]
        matched_count = sum(1 for s in req_skills if user_skills_dict.get(s, 0) > 0)
        match_score = round((matched_count / len(req_skills)) * 100) if req_skills else 0
        recommended.append({
            **dict(item),
            "match_score": match_score,
            "req_skills_list": req_skills
        })
    recommended.sort(key=lambda x: x['match_score'], reverse=True)

    # User applications status count
    app_stats = query_db("""
        SELECT status, COUNT(*) as count FROM applications 
        WHERE user_id = ? GROUP BY status
    """, [session['user_id']])
    app_summary = {row['status']: row['count'] for row in app_stats}

    return render_template(
        'dashboard.html',
        user=user,
        target_role=target_role,
        user_skills=user_skills_raw,
        user_skills_dict=user_skills_dict,
        analysis=analysis,
        projects=projects,
        badges=badges,
        milestones=milestones,
        recommended=recommended[:4],
        app_summary=app_summary
    )

@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    headline = data.get('headline', '').strip()
    education = data.get('education', '').strip()
    institution = data.get('institution', '').strip()
    graduation_year = data.get('graduation_year', '').strip()
    target_role = data.get('target_role', '').strip()
    bio = data.get('bio', '').strip()
    github_url = data.get('github_url', '').strip()
    linkedin_url = data.get('linkedin_url', '').strip()

    if not name:
        return jsonify({"success": False, "error": "Name is required."}), 400

    execute_db("""
        UPDATE users SET
            name = ?, headline = ?, education = ?, institution = ?,
            graduation_year = ?, target_role = ?, bio = ?,
            github_url = ?, linkedin_url = ?
        WHERE id = ?
    """, [name, headline, education, institution, graduation_year, target_role, bio, github_url, linkedin_url, session['user_id']])

    session['user_name'] = name
    return jsonify({"success": True, "message": "Profile updated successfully!"})

@app.route('/api/skills/update', methods=['POST'])
@login_required
def update_skill():
    data = request.get_json(silent=True) or request.form
    skill_name = data.get('skill_name', '').strip()
    try:
        level = max(1, min(5, int(data.get('proficiency_level', 1))))
    except (ValueError, TypeError):
        level = 1

    if not skill_name:
        return jsonify({"success": False, "error": "Skill name is required."}), 400

    existing = query_db("SELECT id FROM user_skills WHERE user_id = ? AND skill_name = ?", [session['user_id'], skill_name], one=True)
    if existing:
        execute_db("UPDATE user_skills SET proficiency_level = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", [level, existing['id']])
    else:
        execute_db("INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES (?, ?, ?)", [session['user_id'], skill_name, level])

    return jsonify({"success": True, "message": f"Updated {skill_name} to level {level}."})

@app.route('/api/skills/delete', methods=['POST'])
@login_required
def delete_skill():
    data = request.get_json(silent=True) or request.form
    skill_name = data.get('skill_name', '').strip()
    if not skill_name:
        return jsonify({"success": False, "error": "Skill name is required."}), 400

    execute_db("DELETE FROM user_skills WHERE user_id = ? AND skill_name = ?", [session['user_id'], skill_name])
    return jsonify({"success": True, "message": f"Removed {skill_name}."})

@app.route('/api/skills/batch', methods=['POST'])
@login_required
def batch_update_skills():
    data = request.get_json(silent=True) or {}
    skills = data.get('skills', [])
    if not isinstance(skills, list):
        return jsonify({"success": False, "error": "Invalid skills format."}), 400

    for item in skills:
        name = item.get('name', '').strip()
        level = max(1, min(5, int(item.get('level', 1))))
        if name:
            existing = query_db("SELECT id FROM user_skills WHERE user_id = ? AND skill_name = ?", [session['user_id'], name], one=True)
            if existing:
                execute_db("UPDATE user_skills SET proficiency_level = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", [level, existing['id']])
            else:
                execute_db("INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES (?, ?, ?)", [session['user_id'], name, level])

    return jsonify({"success": True, "message": f"Imported {len(skills)} skills successfully!"})

@app.route('/api/projects/add', methods=['POST'])
@login_required
def add_project():
    data = request.get_json(silent=True) or request.form
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    tech_stack = data.get('tech_stack', '').strip()
    repo_url = data.get('repo_url', '').strip()
    live_url = data.get('live_url', '').strip()

    if not title or not description:
        return jsonify({"success": False, "error": "Title and description are required."}), 400

    execute_db("""
        INSERT INTO user_projects (user_id, title, description, tech_stack, repo_url, live_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [session['user_id'], title, description, tech_stack, repo_url, live_url])

    # Check if this is their first project, award badge
    proj_count = query_db("SELECT COUNT(*) as c FROM user_projects WHERE user_id = ?", [session['user_id']], one=True)['c']
    if proj_count == 1:
        execute_db("""
            INSERT OR IGNORE INTO user_badges (user_id, badge_name, badge_icon, description)
            VALUES (?, 'Portfolio Creator', 'code-xml', 'Added first showcase project with GitHub & live documentation.')
        """, [session['user_id']])

    return jsonify({"success": True, "message": "Project added successfully!"})

@app.route('/api/projects/delete', methods=['POST'])
@login_required
def delete_project():
    data = request.get_json(silent=True) or request.form
    project_id = data.get('project_id')
    execute_db("DELETE FROM user_projects WHERE id = ? AND user_id = ?", [project_id, session['user_id']])
    return jsonify({"success": True, "message": "Project removed."})

@app.route('/api/milestones/toggle', methods=['POST'])
@login_required
def toggle_milestone():
    data = request.get_json(silent=True) or request.form
    milestone_id = data.get('milestone_id')
    current = query_db("SELECT completed FROM skill_milestones WHERE id = ? AND user_id = ?", [milestone_id, session['user_id']], one=True)
    if not current:
        return jsonify({"success": False, "error": "Milestone not found."}), 404

    new_val = 0 if current['completed'] == 1 else 1
    execute_db("UPDATE skill_milestones SET completed = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?", [new_val, milestone_id])
    return jsonify({"success": True, "completed": new_val})

# -------------------------------------------------------------
# Skill-Gap Analysis API (for live reactive changes)
# -------------------------------------------------------------

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    role_title = data.get('role', '')
    raw_skills = data.get('skills', [])

    role = query_db("SELECT * FROM job_roles WHERE title = ?", [role_title], one=True)
    if not role:
        return jsonify({"error": "Selected role does not exist."}), 400

    skills_dict = {}
    if isinstance(raw_skills, list):
        for item in raw_skills:
            if isinstance(item, dict) and 'name' in item:
                try:
                    level = max(0, min(5, int(item.get('level', 0))))
                except (ValueError, TypeError):
                    level = 0
                skills_dict[item['name']] = level

    analysis = calculate_readiness(skills_dict, role['id'])
    if not analysis:
        return jsonify({"error": "Failed to analyze skills."}), 500

    # Build roadmap recommendations from learning resources
    missing_and_improve = analysis['missing'] + analysis['improve']
    roadmap = []
    for item in missing_and_improve[:6]:
        resource = query_db("SELECT * FROM learning_resources WHERE skill_name = ? LIMIT 1", [item['name']], one=True)
        roadmap.append({
            "skill": item['name'],
            "current": item['current'],
            "required": item['required'],
            "resource_title": resource['title'] if resource else f"Master {item['name']} Fundamentals",
            "provider": resource['provider'] if resource else "Curated Guide",
            "url": resource['url'] if resource else "https://google.com/search?q=" + item['name']
        })

    # Recommended internships
    internships_raw = query_db("SELECT * FROM internships WHERE role_title = ?", [role_title])
    internships = []
    for job in internships_raw:
        req_list = [s.strip() for s in job['required_skills'].split(',') if s.strip()]
        overlap = sum(1 for s in req_list if skills_dict.get(s, 0) > 0)
        match_score = round((overlap / len(req_list)) * 100) if req_list else 0
        internships.append({
            "id": job['id'],
            "title": job['title'],
            "company": job['company'],
            "mode": job['mode'],
            "location": job['location'],
            "stipend": job['stipend'],
            "skills": req_list,
            "match": match_score,
            "url": job['apply_url']
        })
    internships.sort(key=lambda x: x['match'], reverse=True)

    return jsonify({
        "role": role_title,
        "readiness": analysis['readiness'],
        "matched": analysis['matched'],
        "improve": analysis['improve'],
        "missing": analysis['missing'],
        "radar": analysis['radar'],
        "roadmap": roadmap,
        "internships": internships
    })

# -------------------------------------------------------------
# Learning Hub, Resources, Quizzes & Badges
# -------------------------------------------------------------

@app.route('/learning')
@login_required
def learning():
    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    target_role_title = user['target_role'] or 'Full-Stack Developer'
    target_role = query_db("SELECT * FROM job_roles WHERE title = ?", [target_role_title], one=True)

    # User's current skills
    user_skills_raw = query_db("SELECT * FROM user_skills WHERE user_id = ?", [session['user_id']])
    user_skills_dict = {row['skill_name']: row['proficiency_level'] for row in user_skills_raw}

    # Analysis
    analysis = calculate_readiness(user_skills_dict, target_role['id'] if target_role else 1)

    # Fetch resources organized by skill
    all_resources = query_db("SELECT * FROM learning_resources ORDER BY skill_name ASC, difficulty ASC")

    # Fetch quizzes available
    quizzes = query_db("SELECT id, skill_name, question, option_a, option_b, option_c, option_d FROM skill_quizzes ORDER BY skill_name ASC")

    # User badges
    badges = query_db("SELECT * FROM user_badges WHERE user_id = ? ORDER BY earned_at DESC", [session['user_id']])

    # User milestones
    milestones = query_db("SELECT * FROM skill_milestones WHERE user_id = ? ORDER BY completed ASC", [session['user_id']])

    return render_template(
        'learning.html',
        user=user,
        target_role=target_role,
        analysis=analysis,
        resources=all_resources,
        quizzes=quizzes,
        badges=badges,
        milestones=milestones
    )

@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.get_json(silent=True) or request.form
    quiz_id = data.get('quiz_id')
    selected_option = data.get('selected_option', '').strip().upper()

    quiz = query_db("SELECT * FROM skill_quizzes WHERE id = ?", [quiz_id], one=True)
    if not quiz:
        return jsonify({"success": False, "error": "Quiz question not found."}), 404

    is_correct = (selected_option == quiz['correct_option'])
    reward = None

    if is_correct:
        # Increase or verify skill level for user
        skill_name = quiz['skill_name']
        existing = query_db("SELECT id, proficiency_level FROM user_skills WHERE user_id = ? AND skill_name = ?", [session['user_id'], skill_name], one=True)
        if existing:
            new_level = min(5, existing['proficiency_level'] + 1)
            execute_db("UPDATE user_skills SET proficiency_level = ?, verified = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", [new_level, existing['id']])
        else:
            execute_db("INSERT INTO user_skills (user_id, skill_name, proficiency_level, verified) VALUES (?, ?, 2, 1)", [session['user_id'], skill_name])

        # Award skill badge if not already earned
        badge_name = f"{skill_name} Specialist"
        has_badge = query_db("SELECT id FROM user_badges WHERE user_id = ? AND badge_name = ?", [session['user_id'], badge_name], one=True)
        if not has_badge:
            execute_db("""
                INSERT INTO user_badges (user_id, badge_name, badge_icon, description)
                VALUES (?, ?, 'award', ?)
            """, [session['user_id'], badge_name, f"Demonstrated tested competency in {skill_name} with verified quiz score."])
            reward = f"Earned '{badge_name}' Badge!"

    return jsonify({
        "success": True,
        "correct": is_correct,
        "correct_option": quiz['correct_option'],
        "explanation": quiz['explanation'],
        "reward": reward
    })

# -------------------------------------------------------------
# Internships, Search, Filters, Bookmarks & Application Tracker
# -------------------------------------------------------------

@app.route('/internships')
@login_required
def internships_page():
    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    user_skills_raw = query_db("SELECT * FROM user_skills WHERE user_id = ?", [session['user_id']])
    user_skills_dict = {row['skill_name']: row['proficiency_level'] for row in user_skills_raw}

    # Query params for filters
    search_q = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    mode_filter = request.args.get('mode', '').strip()

    sql = "SELECT * FROM internships WHERE 1=1"
    params = []

    if search_q:
        sql += " AND (title LIKE ? OR company LIKE ? OR required_skills LIKE ? OR location LIKE ?)"
        wildcard = f"%{search_q}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    if role_filter:
        sql += " AND role_title = ?"
        params.append(role_filter)

    if mode_filter:
        sql += " AND mode = ?"
        params.append(mode_filter)

    sql += " ORDER BY id DESC"
    all_internships = query_db(sql, params)

    # User's bookmarks set
    bookmarks = {row['internship_id'] for row in query_db("SELECT internship_id FROM bookmarks WHERE user_id = ?", [session['user_id']])}

    # User's applications dict: { internship_id: application_row }
    user_apps = {row['internship_id']: dict(row) for row in query_db("SELECT * FROM applications WHERE user_id = ?", [session['user_id']])}

    # Process match scores
    processed = []
    for item in all_internships:
        req_skills = [s.strip() for s in item['required_skills'].split(',') if s.strip()]
        matched_skills = [s for s in req_skills if user_skills_dict.get(s, 0) > 0]
        missing_skills = [s for s in req_skills if user_skills_dict.get(s, 0) == 0]
        match_score = round((len(matched_skills) / len(req_skills)) * 100) if req_skills else 0

        processed.append({
            **dict(item),
            "match_score": match_score,
            "req_skills_list": req_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "is_bookmarked": item['id'] in bookmarks,
            "application": user_apps.get(item['id'])
        })

    # Sort by match score if no explicit text search
    if not search_q:
        processed.sort(key=lambda x: x['match_score'], reverse=True)

    # Get application tracker list with joined internship details
    tracked_apps = query_db("""
        SELECT a.id as app_id, a.status, a.applied_date, a.notes, 
               i.id as internship_id, i.title, i.company, i.role_title, i.mode, i.deadline, i.apply_url, i.stipend
        FROM applications a
        JOIN internships i ON a.internship_id = i.id
        WHERE a.user_id = ?
        ORDER BY a.updated_at DESC
    """, [session['user_id']])

    return render_template(
        'internships.html',
        internships=processed,
        tracked_apps=tracked_apps,
        search_q=search_q,
        role_filter=role_filter,
        mode_filter=mode_filter,
        bookmarks=bookmarks
    )

@app.route('/api/internships/bookmark', methods=['POST'])
@login_required
def toggle_bookmark():
    data = request.get_json(silent=True) or request.form
    internship_id = data.get('internship_id')
    if not internship_id:
        return jsonify({"success": False, "error": "Internship ID required."}), 400

    existing = query_db("SELECT id FROM bookmarks WHERE user_id = ? AND internship_id = ?", [session['user_id'], internship_id], one=True)
    if existing:
        execute_db("DELETE FROM bookmarks WHERE id = ?", [existing['id']])
        return jsonify({"success": True, "bookmarked": False})
    else:
        execute_db("INSERT INTO bookmarks (user_id, internship_id) VALUES (?, ?)", [session['user_id'], internship_id])
        return jsonify({"success": True, "bookmarked": True})

@app.route('/api/applications/apply', methods=['POST'])
@login_required
def apply_internship():
    data = request.get_json(silent=True) or request.form
    internship_id = data.get('internship_id')
    notes = data.get('notes', 'Applied through platform external link.').strip()

    if not internship_id:
        return jsonify({"success": False, "error": "Internship ID required."}), 400

    existing = query_db("SELECT id FROM applications WHERE user_id = ? AND internship_id = ?", [session['user_id'], internship_id], one=True)
    if existing:
        execute_db("UPDATE applications SET status = 'Applied', notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", [notes, existing['id']])
    else:
        execute_db("INSERT INTO applications (user_id, internship_id, status, notes) VALUES (?, ?, 'Applied', ?)", [session['user_id'], internship_id, notes])

    # Check if first application, award badge
    apps_count = query_db("SELECT COUNT(*) as c FROM applications WHERE user_id = ?", [session['user_id']], one=True)['c']
    if apps_count == 1:
        execute_db("""
            INSERT OR IGNORE INTO user_badges (user_id, badge_name, badge_icon, description)
            VALUES (?, 'Opportunity Seeker', 'send', 'Tracked your first internship opportunity on SkillBridge.')
        """, [session['user_id']])

    return jsonify({"success": True, "message": "Internship added to Application Tracker!"})

@app.route('/api/applications/update-status', methods=['POST'])
@login_required
def update_application_status():
    data = request.get_json(silent=True) or request.form
    app_id = data.get('app_id')
    new_status = data.get('status', 'Applied').strip()
    notes = data.get('notes', '').strip()

    valid_statuses = ['Bookmarked', 'Applied', 'Under Review', 'Interview Scheduled', 'Offer Received', 'Not Selected']
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": "Invalid application status."}), 400

    execute_db("""
        UPDATE applications 
        SET status = ?, notes = CASE WHEN ? != '' THEN ? ELSE notes END, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, [new_status, notes, notes, app_id, session['user_id']])

    return jsonify({"success": True, "message": f"Status updated to '{new_status}'."})

@app.route('/api/applications/delete', methods=['POST'])
@login_required
def delete_application():
    data = request.get_json(silent=True) or request.form
    app_id = data.get('app_id')
    execute_db("DELETE FROM applications WHERE id = ? AND user_id = ?", [app_id, session['user_id']])
    return jsonify({"success": True, "message": "Application removed from tracker."})

# -------------------------------------------------------------
# Mock Interview Hub
# -------------------------------------------------------------

@app.route('/interview')
@login_required
def interview_page():
    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    selected_role = request.args.get('role', user['target_role'] or 'Full-Stack Developer')
    
    questions = query_db("SELECT * FROM mock_interviews WHERE role_title = ? ORDER BY id ASC", [selected_role])
    if not questions:
        questions = query_db("SELECT * FROM mock_interviews ORDER BY id ASC")

    return render_template('interview.html', user=user, questions=questions, selected_role=selected_role)

# -------------------------------------------------------------
# AI Career Assistant & Resume Parser Endpoints
# -------------------------------------------------------------

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json(silent=True) or {}
    prompt = data.get('message', '').strip()
    if not prompt:
        return jsonify({"error": "Message cannot be empty."}), 400

    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    user_skills_raw = query_db("SELECT * FROM user_skills WHERE user_id = ?", [session['user_id']])
    user_skills_dict = {row['skill_name']: row['proficiency_level'] for row in user_skills_raw}
    analysis = calculate_readiness(user_skills_dict, user['target_role'])

    context = {
        "target_role": user['target_role'],
        "education": f"{user['education']} at {user['institution']}",
        "readiness": analysis['readiness'] if analysis else 50,
        "matched_skills": [m['name'] for m in analysis['matched']] if analysis else [],
        "improve_skills": [m['name'] for m in analysis['improve']] if analysis else [],
        "missing_skills": [m['name'] for m in analysis['missing']] if analysis else []
    }

    result = get_ai_career_advice(prompt, context)
    return jsonify(result)

@app.route('/api/resume/extract', methods=['POST'])
@login_required
def extract_resume():
    text = ""
    # Check if text was pasted directly
    if request.is_json:
        data = request.get_json(silent=True) or {}
        text = data.get('text', '')
    elif 'resume_file' in request.files:
        file = request.files['resume_file']
        if file.filename != '':
            try:
                # Read plain text / markdown / decoded bytes
                text = file.read().decode('utf-8', errors='ignore')
            except Exception:
                return jsonify({"error": "Unable to decode text file. Please paste text."}), 400
    else:
        text = request.form.get('text', '')

    if not text.strip():
        return jsonify({"error": "No resume text received. Please upload or paste text."}), 400

    extracted = extract_skills_from_text(text)
    return jsonify({
        "success": True,
        "skills_count": len(extracted),
        "skills": extracted
    })

# -------------------------------------------------------------
# Admin Dashboard & Management Portal
# -------------------------------------------------------------

@app.route('/admin')
@admin_required
def admin():
    stats = {
        "students": query_db("SELECT COUNT(*) as c FROM users WHERE role = 'student'", one=True)['c'],
        "roles": query_db("SELECT COUNT(*) as c FROM job_roles", one=True)['c'],
        "internships": query_db("SELECT COUNT(*) as c FROM internships", one=True)['c'],
        "applications": query_db("SELECT COUNT(*) as c FROM applications", one=True)['c'],
        "resources": query_db("SELECT COUNT(*) as c FROM learning_resources", one=True)['c']
    }

    roles = query_db("SELECT * FROM job_roles ORDER BY id ASC")
    internships = query_db("SELECT * FROM internships ORDER BY id DESC")
    resources = query_db("SELECT * FROM learning_resources ORDER BY id DESC")
    students = query_db("SELECT id, name, email, target_role, created_at FROM users WHERE role = 'student' ORDER BY id DESC")

    return render_template(
        'admin.html',
        stats=stats,
        roles=roles,
        internships=internships,
        resources=resources,
        students=students
    )

@app.route('/api/admin/roles/add', methods=['POST'])
@admin_required
def admin_add_role():
    data = request.get_json(silent=True) or request.form
    title = data.get('title', '').strip()
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    avg_stipend = data.get('avg_stipend', '₹20,000 / mo').strip()
    demand_level = data.get('demand_level', 'High').strip()

    if not title or not category or not description:
        return jsonify({"success": False, "error": "All fields required."}), 400

    try:
        execute_db("""
            INSERT INTO job_roles (title, category, description, avg_stipend, demand_level)
            VALUES (?, ?, ?, ?, ?)
        """, [title, category, description, avg_stipend, demand_level])
        return jsonify({"success": True, "message": f"Job role '{title}' added successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Job role already exists."}), 400

@app.route('/api/admin/internships/add', methods=['POST'])
@admin_required
def admin_add_internship():
    data = request.get_json(silent=True) or request.form
    title = data.get('title', '').strip()
    company = data.get('company', '').strip()
    role_title = data.get('role_title', '').strip()
    location = data.get('location', '').strip()
    mode = data.get('mode', 'Remote').strip()
    stipend = data.get('stipend', '₹20,000 / mo').strip()
    duration = data.get('duration', '3 Months').strip()
    deadline = data.get('deadline', '2026-12-31').strip()
    required_skills = data.get('required_skills', '').strip()
    description = data.get('description', '').strip()
    apply_url = data.get('apply_url', 'https://example.com/demo-apply').strip()

    if not title or not company or not role_title or not required_skills:
        return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

    execute_db("""
        INSERT INTO internships (title, company, role_title, location, mode, stipend, duration, deadline, required_skills, description, apply_url, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, [title, company, role_title, location, mode, stipend, duration, deadline, required_skills, description, apply_url])

    return jsonify({"success": True, "message": "Internship opportunity added successfully!"})

@app.route('/api/admin/internships/delete', methods=['POST'])
@admin_required
def admin_delete_internship():
    data = request.get_json(silent=True) or request.form
    internship_id = data.get('id')
    execute_db("DELETE FROM internships WHERE id = ?", [internship_id])
    return jsonify({"success": True, "message": "Internship deleted successfully."})

@app.route('/api/admin/resources/add', methods=['POST'])
@admin_required
def admin_add_resource():
    data = request.get_json(silent=True) or request.form
    skill_name = data.get('skill_name', '').strip()
    title = data.get('title', '').strip()
    provider = data.get('provider', '').strip()
    rtype = data.get('type', 'Tutorial').strip()
    url = data.get('url', '').strip()
    difficulty = data.get('difficulty', 'Beginner').strip()
    try:
        hours = int(data.get('est_hours', 5))
    except (ValueError, TypeError):
        hours = 5

    if not skill_name or not title or not url:
        return jsonify({"success": False, "error": "Skill, title, and URL are required."}), 400

    execute_db("""
        INSERT INTO learning_resources (skill_name, title, provider, type, url, difficulty, est_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [skill_name, title, provider, rtype, url, difficulty, hours])

    return jsonify({"success": True, "message": "Learning resource added successfully!"})

@app.route('/api/admin/resources/delete', methods=['POST'])
@admin_required
def admin_delete_resource():
    data = request.get_json(silent=True) or request.form
    res_id = data.get('id')
    execute_db("DELETE FROM learning_resources WHERE id = ?", [res_id])
    return jsonify({"success": True, "message": "Resource removed."})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
