from django import forms
from settings.models import ProductGroup, PRODUCTS_CHOICES
from .models import PurchasingCode


class URLBulkCreateForm(forms.Form):
    count = forms.IntegerField(label="Quantity", min_value=1)


class CodeBulkCreateForm(forms.ModelForm):
    count = forms.IntegerField(label="Quantity", min_value=1)
    product = forms.ChoiceField(
        label="Product", widget=forms.Select(attrs={"class": "custom-select"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group_choices = [
            (group.id, group.title) for group in ProductGroup.objects.all()
        ]
        static_choices = PRODUCTS_CHOICES

        self.fields["product"].choices = group_choices + static_choices

    class Meta:
        model = PurchasingCode
        fields = ["count", "duration"]
        widgets = {
            "duration": forms.Select(attrs={"class": "custom-select"}),
        }
