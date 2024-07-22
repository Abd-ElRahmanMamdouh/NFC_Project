from django.urls import path

from . import views

app_name = "cards"


urlpatterns = [
    path(
        "landingPage/<uidb64>/",
        views.NFCCardView.as_view(),
        name="landing_page",
    ),
    path(
        "landingPage/<uidb64>/<int:pk>/update/",
        views.NFCCardUpdateView.as_view(),
        name="set_password",
    ),
    path(
        "dashboard/",
        views.NFCCardListView.as_view(extra_context={"active": "dashboard"}),
        name="user_dashboard",
    ),
    path("cards-link/<uidb64>/", views.link_new_card, name="link_new_card"),
    path("check_password/<uidb64>/", views.check_password, name="check_password")
]
