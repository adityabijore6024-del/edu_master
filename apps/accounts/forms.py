"""
apps/accounts/forms.py
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, SupportTicket


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Create password", "autocomplete": "new-password"}),
        validators=[validate_password],
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "mobile", "full_name"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "mobile": forms.TextInput(attrs={"placeholder": "Mobile number"}),
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email address", "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Registered email address"})
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New password"}),
        validators=[validate_password],
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"})
    )

    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        return cd


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "username", "mobile", "bio", "profile_photo"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "mobile": forms.TextInput(attrs={"placeholder": "Mobile number"}),
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Tell us about yourself"}),
        }


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email"}),
            "subject": forms.TextInput(attrs={"placeholder": "Brief subject"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe your issue in detail..."}),
        }
