"""apps/tests/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.test_list_view, name="tests_list"),
    path("<uuid:test_id>/start/", views.test_start_view, name="test_start"),
    path("submit/<uuid:attempt_id>/", views.submit_test_view, name="submit_test"),
    path("result/<uuid:attempt_id>/", views.test_result_view, name="test_result"),
]
