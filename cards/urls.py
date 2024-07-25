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
    path("check-password/<uidb64>/", views.check_password, name="check_password"),
    path("update-business-card/<uidb64>/", views.update_business_card, name="update_business_card"),
    path("update-gallery/<uidb64>/", views.update_gallery, name="update_gallery"),
    path("update-redirect-url/<uidb64>/", views.update_redirect_url, name="update_redirect_url"),
    path("update-video-message/<uidb64>/", views.update_video_message, name="update_video_message"),
    path("update-product-viewer/<uidb64>/", views.update_product_viewer, name="update_product_viewer"),
    path("update-pdf-viewer/<uidb64>/", views.update_pdf_viewer, name="update_pdf_viewer"),
    path("update-letter/<uidb64>/", views.update_letter, name="update_letter"),
]
