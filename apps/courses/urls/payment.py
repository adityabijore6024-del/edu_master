"""apps/courses/urls/payment.py"""
from django.urls import path
from apps.courses.views.payment import (
    payment_page_view, create_razorpay_order, verify_payment, payment_success_view
)

urlpatterns = [
    path("<slug:slug>/", payment_page_view, name="payment"),
    path("api/create-order/", create_razorpay_order, name="create_order"),
    path("api/verify/", verify_payment, name="verify_payment"),
    path("success/", payment_success_view, name="payment_success"),
]
