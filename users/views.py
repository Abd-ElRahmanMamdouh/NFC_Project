from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import CustomLoginForm, RegisterForm, UserDetailChangeForm
from .models import AuthToken
from .utils import create_token


class UserHomeView(LoginRequiredMixin, DetailView):
    """User Profile Page"""

    template_name = "user/home.html"

    def get_object(self):
        return self.request.user


class UserUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """User Profile Edit Page"""

    form_class = UserDetailChangeForm
    template_name = "user/user_edit.html"
    success_url = reverse_lazy("users:user_profile")
    success_message = "Details successfully updated"

    def get_object(self):
        return self.request.user


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = "registration/register.html"
    success_url = reverse_lazy("users:user_profile")
    form_class = RegisterForm
    success_message = "Your profile was created successfully"

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        username, password = form.cleaned_data.get("username"), form.cleaned_data.get(
            "password1"
        )
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid


class CustomLoginView(LoginView):
    form_class = CustomLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        token = create_token(self.request.user)
        self.request.session['auth_token'] = str(token)
        return response


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        token = request.session.get('auth_token')
        if token:
            AuthToken.objects.filter(token=token).delete()
        logout(request)
        return super().dispatch(request, *args, **kwargs)
