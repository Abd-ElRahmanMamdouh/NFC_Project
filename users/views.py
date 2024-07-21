from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView
from django.http import HttpResponseRedirect
from .forms import CustomLoginForm, RegisterForm, UserDetailChangeForm
from .models import AuthToken
from .utils import create_token
from hitcount.models import HitCount
from cards.models import NFCCard
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType


class UserHomeView(LoginRequiredMixin, DetailView):
    """User Profile Page"""

    template_name = "user/home.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserHomeView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        content_types = ContentType.objects.all()
        total_hits = 0
        for content_type in content_types:
            hits = HitCount.objects.filter(
                content_type=content_type,
                object_pk__in=NFCCard.objects.filter(user=user).values_list('id', flat=True)
            ).aggregate(total_hits=Sum('hits'))['total_hits']

            if hits:
                total_hits += hits

        context['total_hits'] = total_hits
        return context


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
    #success_url = reverse_lazy("users:user_profile")
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

    def get(self, request, *args, **kwargs):
        url_uuid = request.GET.get('uuid')
        uuid = request.COOKIES.get('uuid')
        if uuid:
            request.session['uuid'] = uuid
        elif url_uuid:
            request.session['uuid'] = url_uuid
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        uuid = self.request.session.get('uuid')
        if uuid:
            url = reverse("cards:link_new_card", args=[uuid])
        else:
            url = reverse('users:user_profile"')
        return  url


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        token = create_token(self.request.user)
        self.request.session['auth_token'] = str(token)
        return response

    def get(self, request, *args, **kwargs):
        url_uuid = request.GET.get('uuid')
        uuid = request.COOKIES.get('uuid')
        if uuid:
            request.session['uuid'] = uuid
        elif url_uuid:
            request.session['uuid'] = url_uuid
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        uuid = self.request.session.get('uuid')
        if uuid:
            url = reverse("cards:link_new_card", args=[uuid])
        else:
            if self.request.user.is_staff or self.request.user.is_superuser:
                url = reverse("admin:index")
            else:
                url = reverse("home")
        return url


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        uuid = request.GET.get('uuid')
        if uuid:
            response = super().dispatch(request, *args, **kwargs)
            response.set_cookie('uuid', uuid, max_age=3600)  # Store for 1 hour
            return response

        token = request.session.get('auth_token')
        if token:
            AuthToken.objects.filter(token=token).delete()
        logout(request)
        return self.get_redirect_response(request)

    def get_redirect_response(self, request):
        uuid = request.COOKIES.get('uuid')
        if uuid:
            response = HttpResponseRedirect(reverse("users:login"))
            response.delete_cookie('uuid')
            return response
        else:
            return HttpResponseRedirect(reverse("home"))
