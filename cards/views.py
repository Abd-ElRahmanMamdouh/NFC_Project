from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import NFCCard


class NFCCardView(DetailView):
    template_name = "cards/langing_page_detail.html"
    model = NFCCard
    context_object_name = "card"

    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uidb64")
        return get_object_or_404(self.model, uuid=uuid)
