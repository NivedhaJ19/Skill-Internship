import sqlite3
import os
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'platform.db')

def get_db():
    """Get database connection for current request context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db

def query_db(query, args=(), one=False):
    """Execute a read query and return dictionary rows."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute an insert/update/delete query and return lastrowid."""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

def init_db():
    """Initialize database schema tables."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        headline TEXT,
        education TEXT,
        institution TEXT,
        graduation_year TEXT,
        target_role TEXT DEFAULT 'Full-Stack Developer',
        bio TEXT,
        github_url TEXT,
        linkedin_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Job Roles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        demand_level TEXT DEFAULT 'High',
        avg_stipend TEXT DEFAULT '₹15,000 - ₹35,000 / mo',
        icon TEXT DEFAULT 'code'
    )
    """)

    # Role Required Skills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        required_level INTEGER NOT NULL DEFAULT 3,
        weight INTEGER NOT NULL DEFAULT 3,
        category TEXT DEFAULT 'Technical',
        FOREIGN KEY (role_id) REFERENCES job_roles(id) ON DELETE CASCADE,
        UNIQUE(role_id, skill_name)
    )
    """)

    # User Skills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        proficiency_level INTEGER NOT NULL DEFAULT 1,
        verified INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, skill_name)
    )
    """)

    # User Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        tech_stack TEXT NOT NULL,
        repo_url TEXT,
        live_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Internships Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        role_title TEXT NOT NULL,
        location TEXT NOT NULL,
        mode TEXT NOT NULL,
        stipend TEXT NOT NULL,
        duration TEXT NOT NULL,
        deadline TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        description TEXT NOT NULL,
        apply_url TEXT NOT NULL,
        is_sample INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Learning Resources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL,
        title TEXT NOT NULL,
        provider TEXT NOT NULL,
        type TEXT NOT NULL,
        url TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Beginner',
        est_hours INTEGER DEFAULT 5
    )
    """)

    # Skill Milestones Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        milestone_title TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Skill Quizzes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL,
        explanation TEXT
    )
    """)

    # User Badges Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        badge_name TEXT NOT NULL,
        badge_icon TEXT NOT NULL,
        description TEXT NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, badge_name)
    )
    """)

    # Internship Applications & Tracking Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        internship_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Applied',
        applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
        UNIQUE(user_id, internship_id)
    )
    """)

    # Bookmarks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        internship_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
        UNIQUE(user_id, internship_id)
    )
    """)

    # Mock Interviews Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_title TEXT NOT NULL,
        question TEXT NOT NULL,
        category TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        sample_answer_guide TEXT NOT NULL,
        key_points TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Database schema successfully initialized.")

if __name__ == '__main__':
    init_db()
