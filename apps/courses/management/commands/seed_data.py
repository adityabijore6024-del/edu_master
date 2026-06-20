"""
apps/courses/management/commands/seed_data.py

Populates the database with demo categories, teachers, courses, a sample
test, and achievement badges so the platform looks complete out of the box.

Run with:  python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from apps.courses.models import (
    Category, TeacherProfile, Course, CourseSection, Lecture,
)
from apps.tests.models import Test, Question, QuestionOption
from apps.achievements.models import Badge, INITIAL_BADGES

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo data for EduPeak."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding EduPeak demo data..."))

        self._seed_categories()
        teachers = self._seed_teachers()
        courses = self._seed_courses(teachers)
        self._seed_test(courses)
        self._seed_badges()

        self.stdout.write(self.style.SUCCESS("✔ Demo data seeded successfully!"))

    def _seed_categories(self):
        categories = [
            ("Mathematics", "bi-calculator", "#6366f1"),
            ("Physics", "bi-magnet", "#f59e0b"),
            ("Chemistry", "bi-droplet-half", "#10b981"),
            ("Biology", "bi-flower1", "#ec4899"),
            ("Computer Science", "bi-cpu", "#3b82f6"),
            ("English", "bi-book", "#8b5cf6"),
            ("Reasoning", "bi-puzzle", "#ef4444"),
            ("General Knowledge", "bi-globe", "#14b8a6"),
        ]
        for i, (name, icon, color) in enumerate(categories):
            Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name), "icon": icon, "color": color, "order": i},
            )
        self.stdout.write(f"  Categories: {Category.objects.count()}")

    def _seed_teachers(self):
        teacher_data = [
            ("aditi.sharma@edupeak.com", "aditi_sharma", "Aditi Sharma", "IIT Bombay · 8 yrs experience", "Mathematics, Physics"),
            ("rahul.verma@edupeak.com", "rahul_verma", "Rahul Verma", "AIIMS Delhi · 10 yrs experience", "Biology, Chemistry"),
            ("sneha.iyer@edupeak.com", "sneha_iyer", "Sneha Iyer", "IIT Delhi · 6 yrs experience", "Computer Science"),
            ("vikram.singh@edupeak.com", "vikram_singh", "Vikram Singh", "Cambridge · 12 yrs experience", "English, Reasoning"),
        ]
        teachers = []
        for email, username, full_name, designation, subjects in teacher_data:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "full_name": full_name,
                    "role": User.Role.TEACHER,
                },
            )
            if not user.has_usable_password():
                user.set_password("EduPeak@2025")
                user.save()
            profile, _ = TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "designation": designation,
                    "subjects": subjects,
                    "total_students": 1200,
                    "is_featured": True,
                },
            )
            teachers.append(profile)
        self.stdout.write(f"  Teachers: {len(teachers)}")
        return teachers

    def _seed_courses(self, teachers):
        if not teachers:
            return []

        math_cat = Category.objects.filter(name="Mathematics").first()
        physics_cat = Category.objects.filter(name="Physics").first()
        cs_cat = Category.objects.filter(name="Computer Science").first()

        course_data = [
            {
                "title": "Complete JEE Mathematics Mastery",
                "teacher": teachers[0],
                "category": math_cat,
                "original_price": 4999,
                "discounted_price": 2999,
                "is_featured": True,
                "short_description": "Master calculus, algebra and coordinate geometry for JEE Main & Advanced.",
                "description": "A complete, structured course covering the entire JEE Mathematics syllabus with concept videos, practice problems and full-length mock tests.",
                "what_you_learn": "Calculus fundamentals\nAlgebra & complex numbers\nCoordinate geometry\nProbability & statistics",
                "requirements": "Class 11/12 Mathematics basics\nA notebook for practice",
            },
            {
                "title": "Physics for NEET & JEE Foundations",
                "teacher": teachers[0],
                "category": physics_cat,
                "original_price": 3999,
                "discounted_price": 1999,
                "is_featured": True,
                "short_description": "Build strong fundamentals in mechanics, electromagnetism and modern physics.",
                "description": "Covers the complete Physics syllabus with animated explanations and numerical problem-solving sessions.",
                "what_you_learn": "Mechanics & motion\nElectromagnetism\nThermodynamics\nModern physics",
                "requirements": "Basic algebra",
            },
            {
                "title": "Python Programming for Beginners",
                "teacher": teachers[2],
                "category": cs_cat,
                "original_price": 1999,
                "discounted_price": 0,
                "is_free": True,
                "is_featured": True,
                "short_description": "Learn Python from scratch with hands-on coding exercises.",
                "description": "A beginner-friendly introduction to Python programming, covering syntax, data structures, and real projects.",
                "what_you_learn": "Python syntax & data types\nFunctions & OOP\nFile handling\nMini projects",
                "requirements": "No prior coding experience needed",
            },
        ]

        courses = []
        for data in course_data:
            course, created = Course.objects.get_or_create(
                title=data["title"],
                defaults={**data, "slug": slugify(data["title"]), "is_active": True},
            )
            courses.append(course)
            if created:
                self._seed_sections(course)
        self.stdout.write(f"  Courses: {len(courses)}")
        return courses

    def _seed_sections(self, course):
        section_titles = ["Introduction", "Core Concepts", "Advanced Topics"]
        for i, title in enumerate(section_titles):
            section = CourseSection.objects.create(course=course, title=title, order=i)
            for j in range(1, 4):
                Lecture.objects.create(
                    section=section,
                    title=f"{title} – Lecture {j}",
                    content_type=Lecture.ContentType.VIDEO,
                    video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                    duration_minutes=15 + j * 5,
                    is_preview=(i == 0 and j == 1),
                    order=j,
                )

    def _seed_test(self, courses):
        if not courses:
            return
        test, created = Test.objects.get_or_create(
            title="Mathematics Quick Assessment",
            defaults={
                "course": courses[0],
                "description": "A short diagnostic test covering algebra and calculus basics.",
                "duration_minutes": 15,
                "total_marks": 12,
                "passing_marks": 6,
                "negative_marks": 1,
                "unlimited_attempts": True,
            },
        )
        if not created:
            return

        q1 = Question.objects.create(
            test=test, text="What is the derivative of x²?",
            question_type=Question.QuestionType.SINGLE, marks=4, order=1,
            explanation="d/dx(x²) = 2x using the power rule.",
        )
        QuestionOption.objects.create(question=q1, label="A", text="x", is_correct=False)
        QuestionOption.objects.create(question=q1, label="B", text="2x", is_correct=True)
        QuestionOption.objects.create(question=q1, label="C", text="x²", is_correct=False)
        QuestionOption.objects.create(question=q1, label="D", text="2", is_correct=False)

        q2 = Question.objects.create(
            test=test, text="Which of the following are prime numbers? (Select all that apply)",
            question_type=Question.QuestionType.MULTIPLE, marks=4, order=2,
            explanation="2, 3, and 7 are prime; 9 = 3×3 is not.",
        )
        QuestionOption.objects.create(question=q2, label="A", text="2", is_correct=True)
        QuestionOption.objects.create(question=q2, label="B", text="9", is_correct=False)
        QuestionOption.objects.create(question=q2, label="C", text="3", is_correct=True)
        QuestionOption.objects.create(question=q2, label="D", text="7", is_correct=True)

        q3 = Question.objects.create(
            test=test, text="What is the value of 12 + 8 × 2?",
            question_type=Question.QuestionType.INTEGER, marks=4, order=3,
            explanation="Order of operations: 8×2=16, then 12+16=28.",
        )
        QuestionOption.objects.create(question=q3, label="A", text="28", is_correct=True)

        self.stdout.write("  Sample test created with 3 questions")

    def _seed_badges(self):
        for badge_data in INITIAL_BADGES:
            Badge.objects.get_or_create(slug=badge_data["slug"], defaults=badge_data)
        self.stdout.write(f"  Badges: {Badge.objects.count()}")
