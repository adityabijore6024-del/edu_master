"""apps/ai_doubt/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.doubt_solver_view, name="ai_doubt"),
    path("ask/", views.ask_doubt, name="ask_doubt"),
    path("session/<uuid:session_id>/", views.doubt_session_view, name="doubt_session"),
]
