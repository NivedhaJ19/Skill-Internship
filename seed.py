import sqlite3
import os
from werkzeug.security import generate_password_hash
from database import DATABASE, init_db

def seed_database():
    """Populates the database with realistic sample data."""
    init_db()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Drop existing tables to allow fresh schema with auto-increment IDs starting at 1
    tables = [
        "applications", "bookmarks", "user_badges", "skill_milestones",
        "user_projects", "user_skills", "learning_resources", "skill_quizzes",
        "mock_interviews", "internships", "role_skills", "job_roles", "users"
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

    # Re-create fresh schema
    init_db()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    print("Populating seed users...")
    password_hash = generate_password_hash("student123")
    admin_password_hash = generate_password_hash("admin123")

    users_data = [
        (
            1, "Alex Rivera", "student@demo.edu", password_hash, "student",
            "Aspiring Full-Stack Software Engineer | CS Junior",
            "B.Tech in Computer Science & Engineering", "National Institute of Technology", "2026",
            "Full-Stack Developer",
            "Passionate about building scalable web applications and intuitive student productivity tools. Currently expanding backend architecture knowledge.",
            "https://github.com/alexrivera-demo", "https://linkedin.com/in/alexrivera-demo"
        ),
        (
            2, "Platform Administrator", "admin@skillbridge.edu", admin_password_hash, "admin",
            "Curriculum & Internship Program Director",
            "M.S. in Computer Science", "SkillBridge University", "2018",
            "Full-Stack Developer",
            "Oversees skills taxonomy, learning pathways, and employer demo partnerships.",
            "https://github.com/skillbridge", "https://linkedin.com/company/skillbridge"
        ),
        (
            3, "Priya Sharma", "priya@demo.edu", password_hash, "student",
            "Aspiring Data Analyst & Business Intelligence Explorer",
            "B.S. in Data Analytics & Statistics", "Metro State University", "2027",
            "Data Analyst",
            "Eager to turn raw data into strategic business insights using SQL, Python, and interactive dashboards.",
            "https://github.com/priyasharma-demo", "https://linkedin.com/in/priyasharma-demo"
        )
    ]

    cursor.executemany("""
    INSERT INTO users (id, name, email, password_hash, role, headline, education, institution, graduation_year, target_role, bio, github_url, linkedin_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    print("Populating job roles...")
    job_roles_data = [
        (1, "Full-Stack Developer", "Software Engineering", "Builds end-to-end web applications combining responsive client frontends with reliable server APIs, databases, and deployment pipelines.", "Very High", "₹20,000 - ₹40,000 / mo", "code"),
        (2, "Data Analyst", "Data & Analytics", "Extracts, transforms, and analyzes structured datasets to identify trends, forecast performance, and build executive intelligence dashboards.", "High", "₹18,000 - ₹35,000 / mo", "bar-chart-2"),
        (3, "AI/ML Engineer", "Artificial Intelligence", "Designs and trains machine learning models, handles feature engineering, and deploys predictive inference systems.", "Very High", "₹25,000 - ₹50,000 / mo", "cpu"),
        (4, "Cybersecurity Analyst", "Security & Infrastructure", "Monitors networks, identifies vulnerabilities, performs log audits, and protects systems from intrusion and unauthorized access.", "High", "₹20,000 - ₹42,000 / mo", "shield"),
        (5, "UI/UX Designer", "Product & Design", "Conducts user research, crafts wireframes, designs polished interactive prototypes, and builds scalable design systems.", "Growing", "₹15,000 - ₹32,000 / mo", "layout"),
        (6, "Cloud & DevOps Engineer", "Infrastructure & Operations", "Automates CI/CD delivery pipelines, manages containerized services, and maintains scalable cloud infrastructure.", "Very High", "₹22,000 - ₹45,000 / mo", "cloud")
    ]

    cursor.executemany("""
    INSERT INTO job_roles (id, title, category, description, demand_level, avg_stipend, icon)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, job_roles_data)

    print("Populating role skill benchmarks...")
    role_skills_data = [
        # Full-Stack Developer
        (1, "HTML & CSS", 4, 3, "Frontend"),
        (1, "JavaScript", 5, 5, "Frontend"),
        (1, "React", 4, 4, "Frontend"),
        (1, "SQL", 3, 4, "Database"),
        (1, "Backend APIs", 4, 5, "Backend"),
        (1, "Git & GitHub", 3, 3, "Tools"),
        (1, "Node.js / Python", 4, 4, "Backend"),
        (1, "RESTful Architecture", 3, 3, "Backend"),

        # Data Analyst
        (2, "SQL", 5, 5, "Database"),
        (2, "Excel", 4, 4, "Analysis"),
        (2, "Python", 4, 4, "Programming"),
        (2, "Data Visualization", 4, 4, "BI & Storytelling"),
        (2, "Pandas", 4, 4, "Data Processing"),
        (2, "Statistics", 3, 3, "Mathematics"),
        (2, "Power BI / Tableau", 3, 3, "BI Tools"),

        # AI/ML Engineer
        (3, "Python", 5, 5, "Programming"),
        (3, "Machine Learning", 4, 5, "Core AI"),
        (3, "Statistics", 4, 4, "Mathematics"),
        (3, "Data Structures", 3, 3, "Core CS"),
        (3, "Pandas & NumPy", 4, 4, "Data Processing"),
        (3, "Deep Learning", 3, 4, "Advanced AI"),
        (3, "Model Deployment", 3, 3, "MLOps"),

        # Cybersecurity Analyst
        (4, "Networking", 4, 5, "Infrastructure"),
        (4, "Linux", 4, 4, "Operating Systems"),
        (4, "Security Fundamentals", 5, 5, "Core Security"),
        (4, "Python", 3, 3, "Scripting"),
        (4, "Log Analysis", 3, 4, "Operations"),
        (4, "Vulnerability Assessment", 3, 4, "Auditing"),

        # UI/UX Designer
        (5, "Figma", 5, 5, "Design Tools"),
        (5, "Wireframing", 4, 4, "UX Design"),
        (5, "Prototyping", 4, 4, "Interaction"),
        (5, "User Research", 4, 4, "Research"),
        (5, "Visual Design", 4, 4, "UI Design"),
        (5, "Design Systems", 3, 3, "Standards"),

        # Cloud & DevOps Engineer
        (6, "Linux", 4, 5, "Operating Systems"),
        (6, "Docker & Containers", 4, 5, "Cloud Tools"),
        (6, "CI/CD Pipelines", 3, 4, "Automation"),
        (6, "Git & GitHub", 4, 3, "Tools"),
        (6, "AWS / Azure Basics", 3, 4, "Cloud Provider"),
        (6, "Infrastructure as Code", 3, 3, "Automation")
    ]

    cursor.executemany("""
    INSERT INTO role_skills (role_id, skill_name, required_level, weight, category)
    VALUES (?, ?, ?, ?, ?)
    """, role_skills_data)

    print("Populating initial student skills...")
    # Alex Rivera's current skills
    user_skills_data = [
        (1, "HTML & CSS", 4, 1),
        (1, "JavaScript", 4, 1),
        (1, "React", 3, 0),
        (1, "SQL", 2, 0),
        (1, "Git & GitHub", 3, 1),
        (1, "Backend APIs", 2, 0),
        (1, "Node.js / Python", 2, 0),
        # Priya Sharma's current skills
        (3, "SQL", 4, 1),
        (3, "Excel", 4, 1),
        (3, "Python", 3, 0),
        (3, "Data Visualization", 3, 0),
        (3, "Statistics", 3, 1)
    ]

    cursor.executemany("""
    INSERT INTO user_skills (user_id, skill_name, proficiency_level, verified)
    VALUES (?, ?, ?, ?)
    """, user_skills_data)

    print("Populating student projects...")
    projects_data = [
        (
            1, "CampusCourse Tracker",
            "A responsive web app that allows college students to organize course schedules, track assignment deadlines, and calculate semester GPA.",
            "HTML & CSS, JavaScript, React, LocalStorage",
            "https://github.com/alexrivera-demo/campus-course-tracker",
            "https://campus-tracker-demo.web.app"
        ),
        (
            1, "DevBook REST API",
            "A lightweight backend service providing RESTful endpoints for developer book reviews, user authentication, and ratings.",
            "Python, Flask, SQLite, JWT",
            "https://github.com/alexrivera-demo/devbook-api",
            "https://devbook-api-demo.render.com"
        ),
        (
            3, "E-Commerce Customer Churn Analysis",
            "Exploratory data analysis of 10,000 retail customer records to pinpoint early signs of attrition and visualize lifetime value clusters.",
            "Python, Pandas, Seaborn, SQL",
            "https://github.com/priyasharma-demo/ecommerce-churn",
            "https://priyasharma-demo.github.io/ecommerce-churn"
        )
    ]

    cursor.executemany("""
    INSERT INTO user_projects (user_id, title, description, tech_stack, repo_url, live_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, projects_data)

    print("Populating sample internships (clearly labeled as demo opportunities)...")
    internships_data = [
        (
            1, "Junior Full-Stack Web Intern", "TechWave Labs",
            "Full-Stack Developer", "Bengaluru, India", "Hybrid",
            "₹25,000 / mo", "6 Months", "2026-11-30",
            "HTML & CSS, JavaScript, React, Backend APIs, Git & GitHub",
            "Assist in engineering responsive frontend interfaces and RESTful service integrations for enterprise SaaS collaboration tools.",
            "https://example.com/apply/techwave-fullstack-demo", 1
        ),
        (
            2, "Frontend Engineering Intern", "AuraCloud Systems",
            "Full-Stack Developer", "Remote (India)", "Remote",
            "₹20,000 / mo", "3 Months", "2026-11-15",
            "HTML & CSS, JavaScript, React, Git & GitHub",
            "Work alongside senior UI engineers to craft accessible design components, optimize web performance, and maintain modern React workflows.",
            "https://example.com/apply/auracloud-frontend-demo", 1
        ),
        (
            3, "Backend & API Engineering Intern", "NexusForge Solutions",
            "Full-Stack Developer", "Hyderabad, India", "On-site",
            "₹22,000 / mo", "6 Months", "2026-12-05",
            "Node.js / Python, Backend APIs, SQL, RESTful Architecture",
            "Build robust API microservices, write unit tests, design database schemas, and optimize database querying performance.",
            "https://example.com/apply/nexusforge-backend-demo", 1
        ),
        (
            4, "Business Intelligence & Data Intern", "InsightMatrix Analytics",
            "Data Analyst", "Mumbai, India", "Hybrid",
            "₹18,000 / mo", "4 Months", "2026-11-20",
            "SQL, Excel, Data Visualization, Power BI / Tableau",
            "Cleanse incoming operational data, generate automated weekly KPI reports, and craft executive dashboards for business stakeholders.",
            "https://example.com/apply/insightmatrix-data-demo", 1
        ),
        (
            5, "Product Analytics Intern", "FinTrend Media",
            "Data Analyst", "Remote (India)", "Remote",
            "₹20,000 / mo", "3 Months", "2026-11-25",
            "SQL, Python, Pandas, Statistics",
            "Analyze user retention funnels, perform A/B test statistical analysis, and assist in synthesizing user behavior telemetry.",
            "https://example.com/apply/fintrend-analytics-demo", 1
        ),
        (
            6, "Machine Learning Research Intern", "NeuroVision Intelligence",
            "AI/ML Engineer", "Bengaluru, India", "Hybrid",
            "₹30,000 / mo", "6 Months", "2026-12-15",
            "Python, Machine Learning, Statistics, Pandas & NumPy",
            "Preprocess large computer vision datasets, benchmark baseline ML algorithms, and support production model evaluation experiments.",
            "https://example.com/apply/neurovision-aiml-demo", 1
        ),
        (
            7, "Applied AI Engineering Intern", "Synthetix AI",
            "AI/ML Engineer", "Remote (India)", "Remote",
            "₹28,000 / mo", "4 Months", "2026-11-18",
            "Python, Machine Learning, Deep Learning, Model Deployment",
            "Fine-tune generative and NLP pipelines, deploy lightweight inference endpoints, and write latency evaluation benchmarks.",
            "https://example.com/apply/synthetix-ai-demo", 1
        ),
        (
            8, "Cyber Security Operations Intern (SOC)", "ShieldGuard CyberDefend",
            "Cybersecurity Analyst", "Pune, India", "On-site",
            "₹22,000 / mo", "6 Months", "2026-11-28",
            "Networking, Linux, Security Fundamentals, Log Analysis",
            "Monitor SIEM alerts, identify anomalous traffic patterns, assist incident response teams, and document security event tickets.",
            "https://example.com/apply/shieldguard-cyber-demo", 1
        ),
        (
            9, "Vulnerability Assessment Intern", "SecureStack Global",
            "Cybersecurity Analyst", "Remote (India)", "Remote",
            "₹20,000 / mo", "3 Months", "2026-12-01",
            "Linux, Security Fundamentals, Python, Vulnerability Assessment",
            "Run automated vulnerability scanning tools, verify false positives, and draft remediation recommendations for engineering teams.",
            "https://example.com/apply/securestack-audit-demo", 1
        ),
        (
            10, "UI/UX Product Design Intern", "PixelCraft Studios",
            "UI/UX Designer", "Remote (India)", "Remote",
            "₹18,000 / mo", "3 Months", "2026-11-12",
            "Figma, Wireframing, Prototyping, Visual Design",
            "Conduct student user interviews, create wireframes in Figma, and build interactive design prototypes for educational software products.",
            "https://example.com/apply/pixelcraft-uiux-demo", 1
        ),
        (
            11, "Design Systems & Interaction Intern", "VividStudio Co.",
            "UI/UX Designer", "Bengaluru, India", "Hybrid",
            "₹20,000 / mo", "6 Months", "2026-12-10",
            "Figma, Design Systems, Prototyping, User Research",
            "Collaborate with product managers and engineers to maintain unified Figma component libraries and accessible design guidelines.",
            "https://example.com/apply/vividstudio-design-demo", 1
        ),
        (
            12, "Cloud Infrastructure Intern", "ScaleOps Technologies",
            "Cloud & DevOps Engineer", "Hyderabad, India", "Hybrid",
            "₹24,000 / mo", "6 Months", "2026-11-22",
            "Linux, Docker & Containers, Git & GitHub, CI/CD Pipelines",
            "Support migration of legacy services to Docker containers, write GitHub Actions automation workflows, and observe cloud metrics.",
            "https://example.com/apply/scaleops-cloud-demo", 1
        )
    ]

    cursor.executemany("""
    INSERT INTO internships (id, title, company, role_title, location, mode, stipend, duration, deadline, required_skills, description, apply_url, is_sample)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, internships_data)

    print("Populating curated learning resources...")
    resources_data = [
        # Full-Stack & Web
        ("JavaScript", "Modern JavaScript Tutorial (info)", "javascript.info", "Documentation", "https://javascript.info", "Beginner", 20),
        ("JavaScript", "MDN JavaScript Guide", "Mozilla Developer Network", "Documentation", "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "Intermediate", 15),
        ("HTML & CSS", "Responsive Web Design Certification", "freeCodeCamp", "Course", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "Beginner", 25),
        ("React", "Official React Docs & Interactive Tutorial", "React Team", "Interactive Lab", "https://react.dev/learn", "Beginner", 15),
        ("React", "Full Stack Open: Deep Dive Into Modern Web Development", "University of Helsinki", "Course", "https://fullstackopen.com/en/", "Intermediate", 35),
        ("SQL", "SQLBolt - Interactive SQL Lessons", "SQLBolt", "Interactive Lab", "https://sqlbolt.com", "Beginner", 8),
        ("SQL", "Mode Analytics SQL Tutorial for Data Analysis", "Mode", "Tutorial", "https://mode.com/sql-tutorial/", "Intermediate", 12),
        ("Backend APIs", "REST API Tutorial & Best Practices", "RESTfulAPI.net", "Tutorial", "https://restfulapi.net", "Intermediate", 6),
        ("Git & GitHub", "Git Immersion - Guided Tour", "Git Immersion", "Interactive Lab", "https://gitimmersion.com", "Beginner", 4),
        ("Node.js / Python", "Flask Mega-Tutorial by Miguel Grinberg", "Miguel Grinberg", "Project Guide", "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world", "Intermediate", 18),
        
        # Data Analyst & AI
        ("Excel", "Excel Exposure - Free Video Training", "Excel Exposure", "Course", "https://excelexposure.com", "Beginner", 10),
        ("Python", "Python for Everybody (PY4E)", "Dr. Charles Severance", "Course", "https://www.py4e.com", "Beginner", 20),
        ("Data Visualization", "Data Visualization with Python & Seaborn", "Kaggle Learn", "Interactive Lab", "https://www.kaggle.com/learn/data-visualization", "Beginner", 6),
        ("Pandas", "Pandas Cookbook & 10 Minutes to Pandas", "Pandas Official", "Documentation", "https://pandas.pydata.org/docs/user_guide/10min.html", "Intermediate", 8),
        ("Statistics", "Khan Academy Statistics & Probability", "Khan Academy", "Course", "https://www.khanacademy.org/math/statistics-probability", "Beginner", 18),
        ("Machine Learning", "Intro to Machine Learning Course", "Kaggle Learn", "Interactive Lab", "https://www.kaggle.com/learn/intro-to-machine-learning", "Intermediate", 12),
        ("Deep Learning", "Deep Learning Specialization Playbook", "deeplearning.ai", "Course", "https://www.deeplearning.ai", "Advanced", 30),

        # Security
        ("Networking", "Professor Messer's Network+ Study Notes", "Professor Messer", "Course", "https://www.professormesser.com/network-plus/n10-008/n10-008-training-course/", "Beginner", 16),
        ("Linux", "Linux Journey - Interactive Fundamentals", "Linux Journey", "Interactive Lab", "https://linuxjourney.com", "Beginner", 10),
        ("Security Fundamentals", "TryHackMe - Pre-Security Learning Path", "TryHackMe", "Interactive Lab", "https://tryhackme.com/path/outline/presecurity", "Beginner", 15),
        ("Log Analysis", "Splunk Basics & Security Log Analysis", "CyberDefenders", "Project Guide", "https://cyberdefenders.org", "Intermediate", 10),

        # UI/UX Design
        ("Figma", "Figma for Beginners Series", "Figma YouTube", "Tutorial", "https://www.youtube.com/figmadesign", "Beginner", 8),
        ("Wireframing", "Wireframing Academy Guide", "Balsamiq", "Tutorial", "https://balsamiq.com/learn/articles/what-are-wireframes/", "Beginner", 4),
        ("Prototyping", "Interactive Prototyping Best Practices", "Figma Community", "Project Guide", "https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma", "Intermediate", 6),
        ("User Research", "Nielsen Norman Group - UX Research Methods", "NN/g", "Documentation", "https://www.nngroup.com/articles/which-ux-research-methods/", "Intermediate", 12)
    ]

    cursor.executemany("""
    INSERT INTO learning_resources (skill_name, title, provider, type, url, difficulty, est_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, resources_data)

    print("Populating skill quizzes...")
    quizzes_data = [
        (
            "JavaScript", "What is the difference between 'let' and 'const' in modern JavaScript?",
            "'let' is block-scoped and reassignable, while 'const' cannot be reassigned",
            "'const' is function-scoped while 'let' is globally-scoped",
            "'let' can only hold numbers while 'const' holds strings",
            "There is no difference; they are aliases for 'var'",
            "A", "'let' declarations are block-scoped and allow reassignment, whereas 'const' creates an immutable binding to the identifier."
        ),
        (
            "JavaScript", "Which method is commonly used to transform each element of an array into a new array?",
            "filter()", "map()", "reduce()", "forEach()",
            "B", "Array.prototype.map() applies a transformation function to each element and produces a brand new array of equal length."
        ),
        (
            "HTML & CSS", "In modern CSS Flexbox, which property aligns flex items along the main axis?",
            "align-items", "justify-content", "align-content", "flex-direction",
            "B", "'justify-content' governs distribution along the main axis, while 'align-items' governs cross-axis alignment."
        ),
        (
            "React", "What React Hook is used to perform side effects such as data fetching or subscriptions?",
            "useState", "useContext", "useEffect", "useMemo",
            "C", "'useEffect' runs after render cycles to coordinate side effects such as fetching API data, timers, and DOM mutations."
        ),
        (
            "SQL", "Which SQL clause is used to filter rows after an aggregate GROUP BY operation?",
            "WHERE", "ORDER BY", "HAVING", "LIMIT",
            "C", "'HAVING' operates on aggregated groups (e.g. HAVING COUNT(*) > 5), whereas 'WHERE' filters rows before aggregation."
        ),
        (
            "Backend APIs", "Which HTTP status code signifies that a resource was successfully created on the server?",
            "200 OK", "201 Created", "204 No Content", "301 Moved Permanently",
            "B", "HTTP 201 Created indicates the request succeeded and led to the creation of a new resource on the server."
        ),
        (
            "Git & GitHub", "Which Git command records staged snapshots to the local repository commit history?",
            "git add", "git commit -m 'message'", "git push origin main", "git checkout -b",
            "B", "'git commit' saves your staged changes to the local repository with an informative log message."
        ),
        (
            "Python", "Which Python data structure maintains an unordered collection of unique elements?",
            "List", "Tuple", "Dictionary", "Set",
            "D", "A Python 'set' is an unordered collection of unique, hashable items with fast O(1) membership lookups."
        ),
        (
            "Data Visualization", "Which chart type is best suited for visualizing the distribution of a single numerical variable?",
            "Pie Chart", "Histogram", "Scatter Plot", "Radar Chart",
            "B", "Histograms group continuous numerical data into frequency bins to illustrate distribution, skewness, and spread."
        ),
        (
            "Networking", "Which protocol securely maps domain names (e.g., skillbridge.edu) into IP addresses?",
            "DHCP", "DNS", "FTP", "SNMP",
            "B", "DNS (Domain Name System) translates human-readable hostnames into numerical IP addresses."
        ),
        (
            "Figma", "What is the primary benefit of using Auto Layout in Figma?",
            "It automatically colors vector icons",
            "It creates responsive frames that adapt dynamically as content changes or resizes",
            "It generates production-ready backend code",
            "It saves wireframes to PDF format only",
            "B", "Auto Layout replicates CSS Flexbox behavior inside Figma, ensuring buttons, cards, and layouts dynamically adapt."
        )
    ]

    cursor.executemany("""
    INSERT INTO skill_quizzes (skill_name, question, option_a, option_b, option_c, option_d, correct_option, explanation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, quizzes_data)

    print("Populating initial student badges...")
    badges_data = [
        (1, "Web Navigator", "compass", "Completed the HTML & CSS fundamentals readiness assessment."),
        (1, "Git Pioneer", "git-branch", "Demonstrated version control and branching best practices."),
        (1, "Portfolio Builder", "folder-check", "Published first full-stack project with live repository link.")
    ]

    cursor.executemany("""
    INSERT INTO user_badges (user_id, badge_name, badge_icon, description)
    VALUES (?, ?, ?, ?)
    """, badges_data)

    print("Populating student milestones...")
    milestones_data = [
        (1, "JavaScript", "Master ES6+ Destructuring, Promises, and Async/Await", 1),
        (1, "JavaScript", "Build an interactive CRUD DOM application", 1),
        (1, "React", "Build components using useState and useEffect hooks", 1),
        (1, "React", "Connect React app to a real REST API endpoint", 0),
        (1, "SQL", "Write complex queries using INNER & LEFT JOINs", 0),
        (1, "Backend APIs", "Design 5 RESTful endpoints with validation and error handling", 0),
        (1, "Node.js / Python", "Deploy a persistent Flask API service to cloud hosting", 0)
    ]

    cursor.executemany("""
    INSERT INTO skill_milestones (user_id, skill_name, milestone_title, completed)
    VALUES (?, ?, ?, ?)
    """, milestones_data)

    print("Populating applications and bookmarks...")
    applications_data = [
        (1, 1, "Applied", "Applied via university portal with updated resume."),
        (1, 2, "Under Review", "Received automated confirmation; recruiter screening underway.")
    ]
    cursor.executemany("""
    INSERT INTO applications (user_id, internship_id, status, notes)
    VALUES (?, ?, ?, ?)
    """, applications_data)

    bookmarks_data = [
        (1, 3)
    ]
    cursor.executemany("""
    INSERT INTO bookmarks (user_id, internship_id)
    VALUES (?, ?)
    """, bookmarks_data)

    print("Populating mock interview questions...")
    interview_data = [
        # Full-Stack Developer
        (
            "Full-Stack Developer",
            "Explain the difference between synchronous and asynchronous operations in JavaScript, and how the Event Loop handles them.",
            "Technical", "Medium",
            "A strong answer defines the single-threaded nature of JavaScript's call stack. Synchronous code executes immediately and blocks further execution until done. Asynchronous code (e.g. fetch, setTimeout) is delegated to browser Web APIs; once complete, its callback enters the Callback Queue or Microtask Queue (for Promises). The Event Loop checks if the Call Stack is empty before moving queued tasks onto the stack.",
            "Key points: Call stack, Web APIs, Microtask queue vs Task queue, Non-blocking I/O, Event loop tick."
        ),
        (
            "Full-Stack Developer",
            "How do you design a secure RESTful API endpoint that prevents unauthorized access and handles SQL injection?",
            "Technical", "Medium",
            "Address authentication (JWT tokens or secure sessions in HttpOnly cookies), role-based authorization checks, parameterized SQL queries or ORM sanitization, CORS policy restrictions, input validation (e.g. validating payload schemas), and rate limiting to prevent brute-force attacks.",
            "Key points: Parameterized queries, Token validation, Rate limiting, HTTPS, Input sanitization, Least privilege."
        ),
        (
            "Full-Stack Developer",
            "Describe a time you encountered a stubborn bug in a web project. How did you methodically isolate and resolve it?",
            "Behavioral", "Easy",
            "Use the STAR method (Situation, Task, Action, Result). Highlight structured debugging techniques: reading console errors, inspecting network request payloads, writing reproducible minimal test cases, git bisect, or step-through debugging rather than random guesswork.",
            "Key points: STAR framework, Systematic troubleshooting, Root-cause analysis, Verifying regression tests."
        ),

        # Data Analyst
        (
            "Data Analyst",
            "What is the difference between WHERE and HAVING in SQL, and when would you use a window function over a GROUP BY?",
            "Technical", "Medium",
            "WHERE filters rows prior to aggregation, while HAVING filters post-aggregation summaries. Window functions (e.g., ROW_NUMBER(), RANK(), OVER(PARTITION BY...)) allow calculating running totals or rankings across rows while preserving individual record grain, unlike GROUP BY which collapses rows.",
            "Key points: Row filtering vs group filtering, Preserving row grain, PARTITION BY, Aggregation pipeline."
        ),
        (
            "Data Analyst",
            "How do you handle missing or corrupt data when preparing a dataset for stakeholders?",
            "Technical", "Medium",
            "Explain assessing the mechanism of missingness (MCAR, MAR, MNAR). Strategies include imputation (mean/median/mode or regression imputation), row removal if missingness is negligible, flagging imputed values, and explicitly documenting assumptions and limitations to stakeholders.",
            "Key points: Missingness mechanism, Imputation vs dropping, Data integrity validation, Transparent stakeholder reporting."
        ),

        # AI/ML Engineer
        (
            "AI/ML Engineer",
            "Explain the Bias-Variance tradeoff and how regularization helps prevent overfitting.",
            "Technical", "Medium",
            "High bias leads to underfitting (model is too simplistic to capture underlying patterns). High variance leads to overfitting (model learns noise from the training dataset). Regularization techniques (L1 Lasso, L2 Ridge, Dropout) penalize excessive model complexity to encourage generalization on unseen data.",
            "Key points: Underfitting vs overfitting, Generalization error, L1 vs L2 penalties, Cross-validation."
        ),

        # Cybersecurity Analyst
        (
            "Cybersecurity Analyst",
            "What is the difference between symmetric and asymmetric encryption, and how do they work together in HTTPS/TLS?",
            "Technical", "Medium",
            "Symmetric uses one shared key for both encryption and decryption (fast, but secure key exchange is difficult). Asymmetric uses a public key to encrypt and private key to decrypt (secure key exchange, but computationally heavy). In TLS, asymmetric encryption (e.g., RSA or ECDHE) establishes the handshake and securely exchanges a symmetric session key, which encrypts subsequent traffic.",
            "Key points: Public/private keys, Key distribution, TLS Handshake, Performance optimization."
        ),

        # UI/UX Designer
        (
            "UI/UX Designer",
            "Walk me through your design process from receiving a problem statement to delivering high-fidelity developer specs.",
            "Technical", "Medium",
            "Outline Design Thinking: 1) Empathize & Research (interviews, surveys), 2) Define (user personas, problem statement), 3) Ideate (information architecture, user flows), 4) Prototype (low-fi wireframes to interactive Figma components), 5) Test & Validate (usability tests), 6) Dev Handoff (design tokens, edge cases, responsive states).",
            "Key points: User-centered design, Usability testing, Design tokens, Accessibility standards (WCAG)."
        )
    ]

    cursor.executemany("""
    INSERT INTO mock_interviews (role_title, question, category, difficulty, sample_answer_guide, key_points)
    VALUES (?, ?, ?, ?, ?, ?)
    """, interview_data)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
