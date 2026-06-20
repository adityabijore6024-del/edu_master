"""apps/courses/context_processors.py"""
from .models import Category


def categories_processor(request):
    """Inject top-level categories into every template context."""
    return {"nav_categories": Category.objects.filter(is_active=True)[:8]}
