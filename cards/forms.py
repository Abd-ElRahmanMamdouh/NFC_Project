from django import forms
from .models import Product, PurchasingCode


class PurchasingCodeForm(forms.ModelForm):
    class Meta:
        model = PurchasingCode
        fields = "__all__"
        widgets = {
            "group": forms.Select(
                attrs={
                    "id": "group_new_id",
                    "onchange": "get_extra_products(this.value)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            group_products = self.instance.group.products.all()
            self.fields["extra_products"].queryset = Product.objects.exclude(
                id__in=group_products
            )
