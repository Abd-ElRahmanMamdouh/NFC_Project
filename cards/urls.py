from django.urls import path

from . import views

app_name = "cards"


urlpatterns = [
    path(
        "landingPage/<uidb64>/",
        views.NFCCardView.as_view(),
        name="landing_page",
    ),
    path("cards-link/<uidb64>/", views.link_new_card, name="link_new_card")
]
