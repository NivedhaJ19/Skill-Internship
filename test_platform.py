import unittest
import json
from app import app
from database import init_db
from seed import seed_database

class PlatformTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()
        cls.client = app.test_client()

    def test_01_public_landing_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SkillBridge", res.data)
        self.assertIn(b"Full-Stack Developer", res.data)

    def test_02_public_skill_analyze_api(self):
        payload = {
            "role": "Full-Stack Developer",
            "skills": [
                {"name": "HTML & CSS", "level": 4},
                {"name": "JavaScript", "level": 3},
                {"name": "React", "level": 0}
            ]
        }
        res = self.client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('readiness', data)
        self.assertIn('matched', data)
        self.assertIn('missing', data)
        self.assertIn('internships', data)
        self.assertTrue(data['readiness'] > 0)

    def test_03_student_login(self):
        res = self.client.post('/login', data={
            'email': 'student@demo.edu',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Alex Rivera", res.data)

    def test_04_student_dashboard(self):
        # Already logged in via session in client
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Weighted Readiness", res.data)
        self.assertIn(b"Skill Profile Radar", res.data)

    def test_05_update_skill_api(self):
        res = self.client.post('/api/skills/update', data=json.dumps({
            'skill_name': 'Docker & Containers',
            'proficiency_level': 3
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

    def test_06_add_project_api(self):
        res = self.client.post('/api/projects/add', data=json.dumps({
            'title': 'Automated Test Pipeline',
            'description': 'A robust CI testing integration for Flask apps.',
            'tech_stack': 'Python, Flask, PyTest',
            'repo_url': 'https://github.com/alexrivera-demo/test-pipeline',
            'live_url': 'https://test-pipeline.demo.com'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

    def test_07_internship_discovery_and_bookmark(self):
        res = self.client.get('/internships')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Internship Discovery & Tracker", res.data)

        # Toggle bookmark for internship ID 1
        res = self.client.post('/api/internships/bookmark', data=json.dumps({
            'internship_id': 1
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

    def test_08_apply_and_track_status(self):
        # Apply for internship ID 3
        res = self.client.post('/api/applications/apply', data=json.dumps({
            'internship_id': 3,
            'notes': 'Test application submitted.'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

    def test_09_quiz_submission_and_badge_reward(self):
        # Query the first available quiz ID from the database
        import sqlite3
        conn = sqlite3.connect('platform.db')
        row = conn.execute("SELECT id, correct_option FROM skill_quizzes LIMIT 1").fetchone()
        conn.close()
        quiz_id = row[0]
        correct_opt = row[1]

        res = self.client.post('/api/quiz/submit', data=json.dumps({
            'quiz_id': quiz_id,
            'selected_option': correct_opt
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['correct'])
        self.assertIn('explanation', data)

    def test_10_ai_career_chat_mentor(self):
        res = self.client.post('/api/ai/chat', data=json.dumps({
            'message': 'What should I learn next to improve my readiness?'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('reply', data)
        self.assertIn('Strategic Next Steps', data['reply'])

    def test_11_resume_skill_extractor(self):
        resume_text = """
        Alex Rivera - Software Engineer
        Proficient in JavaScript, React, HTML & CSS, and SQL.
        Experienced with Python, Git & GitHub, and building Backend APIs.
        Familiar with Docker and Linux commands.
        """
        res = self.client.post('/api/resume/extract', data=json.dumps({
            'text': resume_text
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        skill_names = [s['name'] for s in data['skills']]
        self.assertIn('JavaScript', skill_names)
        self.assertIn('React', skill_names)
        self.assertIn('SQL', skill_names)

    def test_12_admin_portal_and_crud(self):
        # Log out student
        self.client.get('/logout')

        # Log in as admin
        self.client.post('/login', data={
            'email': 'admin@skillbridge.edu',
            'password': 'admin123'
        }, follow_redirects=True)

        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Administrator Management Hub", res.data)

        # Add internship listing as admin
        res = self.client.post('/api/admin/internships/add', data=json.dumps({
            'title': 'Cloud Security Intern',
            'company': 'CyberApex Systems',
            'role_title': 'Cybersecurity Analyst',
            'location': 'Remote',
            'mode': 'Remote',
            'stipend': '₹28,000 / mo',
            'duration': '6 Months',
            'deadline': '2026-12-31',
            'required_skills': 'Networking, Linux, Security Fundamentals',
            'description': 'Protect cloud infrastructure and audit security alerts.',
            'apply_url': 'https://example.com/apply/cyberapex-demo'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
