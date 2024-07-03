from django import forms
from django.contrib import admin
from .models import NFCCard, ProductGroup, Product, PurchasingCode


class CodeForm(forms.ModelForm):
    class Meta:
        model = PurchasingCode
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Filter the extra_products queryset
            group_products = self.instance.group.products.all()
            self.fields['extra_products'].queryset = Product.objects.exclude(id__in=group_products)
