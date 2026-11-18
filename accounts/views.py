from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .decorators import role_required
from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import Profile


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # password is hashed by Django's UserCreationForm
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("login")
        messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    if request.user.profile.role == Profile.ROLE_ADMIN:
        return redirect("admin_dashboard")
    return redirect("student_dashboard")


@role_required(Profile.ROLE_ADMIN)
def admin_dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "total_students": Profile.objects.filter(role=Profile.ROLE_STUDENT).count(),
        "total_admins": Profile.objects.filter(role=Profile.ROLE_ADMIN).count(),
        "users": User.objects.select_related("profile").order_by("-date_joined"),
    }
    return render(request, "accounts/admin_dashboard.html", context)


@role_required(Profile.ROLE_STUDENT)
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html")


@login_required
def profile_view(request):
    # Always the logged-in user's own profile; no user id in the URL.
    return render(request, "accounts/profile.html", {"profile": request.user.profile})


@login_required
def profile_edit(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("profile")
        messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, "accounts/profile_edit.html", {"user_form": user_form, "profile_form": profile_form})
