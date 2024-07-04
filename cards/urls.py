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
        "admin/filtered-products/<int:group_id>/<int:card_id>/",
        views.filtered_products,
        name="filtered-products",
    ),
]
