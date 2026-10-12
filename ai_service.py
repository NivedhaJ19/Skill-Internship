import os
import re
import json
import urllib.request
import urllib.error

# Standard comprehensive tech skill catalog for resume extraction
KNOWN_SKILLS = [
    # Full-Stack & Web
    "HTML & CSS", "HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Vue.js", "Angular",
    "Node.js", "Express", "Node.js / Python", "Backend APIs", "RESTful Architecture", "GraphQL",
    "SQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Git & GitHub", "Git", "GitHub",
    # Data & Analytics
    "Python", "Excel", "Data Visualization", "Pandas", "NumPy", "Statistics", "Power BI / Tableau",
    "Power BI", "Tableau", "Matplotlib", "Seaborn", "R", "Data Cleaning",
    # AI & ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-Learn", "Model Deployment",
    "Data Structures", "Pandas & NumPy", "NLP", "Computer Vision", "Algorithms",
    # Cybersecurity & Infrastructure
    "Networking", "Linux", "Security Fundamentals", "Log Analysis", "Vulnerability Assessment",
    "Cryptography", "Wireshark", "Bash", "Penetration Testing", "SIEM", "Firewalls",
    # UI / UX Design
    "Figma", "Wireframing", "Prototyping", "User Research", "Visual Design", "Design Systems",
    "User Personas", "Usability Testing", "Adobe XD", "Information Architecture",
    # Cloud & DevOps
    "Docker & Containers", "Docker", "Kubernetes", "CI/CD Pipelines", "CI/CD",
    "AWS / Azure Basics", "AWS", "Azure", "GCP", "Infrastructure as Code", "Terraform"
]

CANONICAL_SKILL_MAP = {
    "html": "HTML & CSS",
    "css": "HTML & CSS",
    "html & css": "HTML & CSS",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "JavaScript",
    "react": "React",
    "reactjs": "React",
    "sql": "SQL",
    "mysql": "SQL",
    "postgresql": "SQL",
    "postgres": "SQL",
    "sqlite": "SQL",
    "backend apis": "Backend APIs",
    "rest apis": "Backend APIs",
    "restful": "RESTful Architecture",
    "restful architecture": "RESTful Architecture",
    "git": "Git & GitHub",
    "github": "Git & GitHub",
    "git & github": "Git & GitHub",
    "nodejs": "Node.js / Python",
    "node.js": "Node.js / Python",
    "node.js / python": "Node.js / Python",
    "excel": "Excel",
    "python": "Python",
    "python3": "Python",
    "statistics": "Statistics",
    "data visualization": "Data Visualization",
    "pandas": "Pandas",
    "pandas & numpy": "Pandas & NumPy",
    "numpy": "Pandas & NumPy",
    "power bi": "Power BI / Tableau",
    "tableau": "Power BI / Tableau",
    "power bi / tableau": "Power BI / Tableau",
    "machine learning": "Machine Learning",
    "data structures": "Data Structures",
    "deep learning": "Deep Learning",
    "model deployment": "Model Deployment",
    "networking": "Networking",
    "linux": "Linux",
    "security fundamentals": "Security Fundamentals",
    "cyber security": "Security Fundamentals",
    "log analysis": "Log Analysis",
    "vulnerability assessment": "Vulnerability Assessment",
    "figma": "Figma",
    "wireframing": "Wireframing",
    "prototyping": "Prototyping",
    "user research": "User Research",
    "visual design": "Visual Design",
    "design systems": "Design Systems",
    "docker": "Docker & Containers",
    "docker & containers": "Docker & Containers",
    "ci/cd": "CI/CD Pipelines",
    "ci/cd pipelines": "CI/CD Pipelines",
    "aws": "AWS / Azure Basics",
    "azure": "AWS / Azure Basics",
    "aws / azure basics": "AWS / Azure Basics",
    "infrastructure as code": "Infrastructure as Code"
}

def extract_skills_from_text(text):
    """
    Parses resume text or summary using keyword and boundary pattern analysis.
    Returns a list of extracted skills with normalized names and estimated levels.
    """
    if not text or not text.strip():
        return []

    lower_text = text.lower()
    found_skills = {}

    for skill in KNOWN_SKILLS:
        skill_lower = skill.lower()
        # Escaping for regex matching
        pattern = r'(?<![a-z0-9])' + re.escape(skill_lower) + r'(?![a-z0-9])'
        match = re.search(pattern, lower_text)
        if match:
            # Check context around match for proficiency hints
            start = max(0, match.start() - 40)
            end = min(len(lower_text), match.end() + 40)
            context = lower_text[start:end]

            level = 3  # Default intermediate
            if any(w in context for w in ["expert", "lead", "advanced", "senior", "proficient", "strong", "5 years", "3 years"]):
                level = 4
            elif any(w in context for w in ["beginner", "basic", "familiar", "exposure", "learning", "elementary"]):
                level = 2

            canonical = CANONICAL_SKILL_MAP.get(skill_lower, skill)
            if canonical not in found_skills or found_skills[canonical] < level:
                found_skills[canonical] = level

    results = [{"name": name, "level": lvl} for name, lvl in found_skills.items()]
    results.sort(key=lambda x: x["name"])
    return results

def get_ai_career_advice(prompt, user_context=None):
    """
    Generates intelligent personalized career advice.
    If GEMINI_API_KEY or OPENAI_API_KEY is available in the environment,
    it attempts the cloud API.
    Otherwise, it reliably uses the built-in Smart Heuristic Career Engine.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            advice = _call_gemini_api(gemini_key, prompt, user_context)
            if advice:
                return {
                    "source": "Gemini AI",
                    "reply": advice
                }
        except Exception as e:
            # Fall back gracefully on error
            pass

    # Built-in Heuristic Career Guidance Engine
    reply = _heuristic_career_mentor(prompt, user_context or {})
    return {
        "source": "Smart Career Assistant (Built-in Heuristic Engine)",
        "reply": reply
    }

def _call_gemini_api(api_key, user_prompt, user_context):
    """Calls Google Gemini API using native Python urllib."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    context_str = ""
    if user_context:
        context_str = f"""
Student Profile Context:
- Target Role: {user_context.get('target_role', 'Software Engineer')}
- Readiness Score: {user_context.get('readiness', 'N/A')}%
- Target Met Skills: {', '.join(user_context.get('matched_skills', []))}
- Skills Needing Work: {', '.join(user_context.get('improve_skills', []))}
- Critical Missing Skills: {', '.join(user_context.get('missing_skills', []))}
- Education: {user_context.get('education', 'College Student')}
"""

    system_instruction = (
        "You are BridgeAI, a warm, professional, actionable Career & Internship Mentor "
        "on the Smart Internship & Skill Mapping Platform. Provide concise, direct, inspiring "
        "advice with concrete action steps, project ideas, and study milestones."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\n{context_str}\n\nStudent Question: {user_prompt}"}
                ]
            }
        ]
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode('utf-8'))
        candidates = res.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
    return None

def _heuristic_career_mentor(prompt, context):
    """
    Intelligent heuristic career mentor that tailors feedback
    to student's target role, current gaps, and specific questions.
    """
    p_lower = prompt.lower()
    target_role = context.get('target_role', 'Full-Stack Developer')
    readiness = context.get('readiness', 65)
    matched = context.get('matched_skills', [])
    improve = context.get('improve_skills', [])
    missing = context.get('missing_skills', [])

    # Intent 1: Roadmap & what to prioritize next
    if any(k in p_lower for k in ["learn", "roadmap", "next", "priority", "improve", "gap", "readiness", "score"]):
        focus_items = missing[:2] + improve[:1]
        focus_str = ", ".join(focus_items) if focus_items else "building full-fledged capstone projects"
        
        reply = (
            f"### 🎯 Strategic Next Steps for {target_role}\n\n"
            f"Your current readiness score is **{readiness}%**. To unlock 85%+ readiness for top internships:\n\n"
            f"1. **Primary High-Impact Focus: {focus_str}**\n"
            f"   - Allocate 45 minutes daily to deliberate practice on these skills.\n"
            f"   - Use interactive tutorials (such as the curated resources in your Learning tab) rather than just passive videos.\n\n"
            f"2. **Validate Through a Mini-Milestone:**\n"
            f"   - Build a small feature that integrates these skills (for example, connect an API endpoint to a database query and display it in a clean UI).\n\n"
            f"3. **Complete the Skill Quiz:**\n"
            f"   - Head over to the **Skill Quizzes** section in your roadmap to verify your competency and earn verified skill badges for your profile.\n\n"
            f"Keep consistent — bridging just 1 or 2 core skill gaps increases your internship match eligibility significantly!"
        )
        return reply

    # Intent 2: Interview preparation
    if any(k in p_lower for k in ["interview", "mock", "question", "prepare", "screening", "hire"]):
        reply = (
            f"### 💼 Interview Prep Blueprint for {target_role}\n\n"
            f"Here is how you can stand out in internship interviews:\n\n"
            f"1. **Master the Fundamentals:**\n"
            f"   - Review core principles for {target_role} (e.g. REST APIs, data structures, asynchronous programming, or system trade-offs).\n"
            f"   - Practice expressing *why* you chose a specific technology over alternatives.\n\n"
            f"2. **Use the STAR Method for Behavioral Questions:**\n"
            f"   - **S**ituation, **T**ask, **A**ction, **R**esult.\n"
            f"   - Prepare 2 specific stories about overcoming a tricky debugging issue or team disagreement.\n\n"
            f"3. **Explore our Mock Interview Hub:**\n"
            f"   - Check the **Mock Interview** tab on the navigation bar. We have tailored technical questions, sample answer guides, and key points for {target_role}!"
        )
        return reply

    # Intent 3: Projects & Portfolio
    if any(k in p_lower for k in ["project", "portfolio", "github", "resume", "build"]):
        reply = (
            f"### 🚀 High-Impact Portfolio Recommendations for {target_role}\n\n"
            f"Recruiters love projects that solve real problems over generic tutorial clones:\n\n"
            f"1. **Recommended Capstone Project Idea:**\n"
            f"   - Build a **Collaborative Workflow or Analytics Tool** that demonstrates:\n"
            f"     - Client-side interactivity and clean UI UX.\n"
            f"     - Secure authentication and persistent database storage.\n"
            f"     - Clean error handling and input validation.\n\n"
            f"2. **GitHub Best Practices:**\n"
            f"   - Write a compelling `README.md` with screenshots, architecture diagrams, and a 1-click live demo link.\n"
            f"   - Add meaningful git commit messages demonstrating iterative development.\n\n"
            f"3. **Profile Integration:**\n"
            f"   - Add your finished project to the **Projects Portfolio** section in your dashboard so it appears on your verified profile!"
        )
        return reply

    # Intent 4: Internship Applications & Strategy
    if any(k in p_lower for k in ["apply", "internship", "stipend", "application", "recommend", "job"]):
        reply = (
            f"### 📌 Internship Search & Application Strategy\n\n"
            f"Based on your profile target for **{target_role}**:\n\n"
            f"1. **Target Opportunities with 60%+ Match:**\n"
            f"   - You don't need 100% of all required skills to apply. Organizations look for strong foundational core skills and high curiosity to learn on the job.\n\n"
            f"2. **Tailor Your Applications:**\n"
            f"   - Highlight your matched skills ({', '.join(matched[:3]) if matched else 'core competencies'}) prominently in your application notes.\n\n"
            f"3. **Track Every Stage:**\n"
            f"   - Use the built-in **Application Tracker** in the Internships tab to monitor your status from *Applied* to *Interview Scheduled* so you never miss a deadline!"
        )
        return reply

    # Default general mentoring response
    reply = (
        f"### 👋 Hello! I'm BridgeAI, your Skill & Career Mentor.\n\n"
        f"You are currently working towards becoming a **{target_role}** with a readiness score of **{readiness}%**.\n\n"
        f"**Here are quick questions you can ask me:**\n"
        f"- *'What specific skill gaps should I learn this week?'*\n"
        f"- *'How can I prepare for a {target_role} technical interview?'*\n"
        f"- *'What capstone project will impress recruiters for {target_role}?'*\n"
        f"- *'How can I improve my match rate for top internships?'*\n\n"
        f"Feel free to ask any question or check your customized roadmap tabs anytime!"
    )
    return reply
