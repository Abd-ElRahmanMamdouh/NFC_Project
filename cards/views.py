from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import NFCCard, Product, ProductGroup, PurchasingCode


class NFCCardView(DetailView):
    template_name = "cards/langing_page_detail.html"
    model = NFCCard
    context_object_name = "card"

    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uidb64")
        return get_object_or_404(self.model, uuid=uuid)


def filtered_products(request, group_id, card_id):
    group = get_object_or_404(ProductGroup, id=group_id)
    group_products = group.products.all()
    if card_id:
        card = get_object_or_404(NFCCard, id=card_id)
        code = get_object_or_404(PurchasingCode, card=card)
        selected_extra_products = Product.objects.filter(product_codes=code)
        if selected_extra_products:
            extra_filtered_products = Product.objects.exclude(
                id__in=group_products.values_list("id", flat=True)
            ).exclude(id__in=selected_extra_products)
            data = list(extra_filtered_products.values("id", "title"))
        else:
            filtered_products = Product.objects.exclude(
                id__in=group_products.values_list("id", flat=True)
            )
            data = list(filtered_products.values("id", "title"))
    else:
        filtered_products = Product.objects.exclude(
            id__in=group_products.values_list("id", flat=True)
        )
        data = list(filtered_products.values("id", "title"))

    return JsonResponse(data, safe=False)
