#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# EduPeak — One-command setup script
# Creates a virtual environment, installs dependencies, generates
# migrations, applies them, seeds demo data, and creates a superuser.
# ════════════════════════════════════════════════════════════════
set -e

echo "════════════════════════════════════════════════"
echo "  EduPeak Platform — Setup"
echo "════════════════════════════════════════════════"

# 1. Create virtual environment
if [ ! -d "venv" ]; then
  echo "→ Creating virtual environment..."
  python3 -m venv venv
fi

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
echo "→ Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 4. Create .env if missing
if [ ! -f ".env" ]; then
  echo "→ Creating .env from .env.example..."
  cp .env.example .env
  echo "  ⚠ Please edit .env and add your ANTHROPIC_API_KEY, RAZORPAY keys, etc."
fi

# 5. Generate & apply migrations
echo "→ Generating migrations..."
python manage.py makemigrations accounts courses tests ai_doubt analytics achievements

echo "→ Applying migrations..."
python manage.py migrate

# 6. Seed demo data
echo "→ Seeding demo data (categories, teachers, courses, badges)..."
python manage.py seed_data

# 7. Create superuser (interactive)
echo "→ Create an admin (superuser) account:"
python manage.py createsuperuser

# 8. Collect static files
echo "→ Collecting static files..."
python manage.py collectstatic --noinput -v 0

echo ""
echo "════════════════════════════════════════════════"
echo "  ✔ Setup complete!"
echo "  Run the server with:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo "  Then open http://127.0.0.1:8000/"
echo "════════════════════════════════════════════════"
