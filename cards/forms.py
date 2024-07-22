from django import forms
from settings.models import ProductGroup, PRODUCTS_CHOICES
from .models import PurchasingCode, NFCCard


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


class NFCCardForm(forms.ModelForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='Old Password'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label='Password'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput()
    )
    class Meta:
        model = NFCCard
        fields = ['old_password', 'password', 'password2']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.password:
            self.fields['old_password'].required = True
        else:
            self.fields.pop('old_password')

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if self.instance and self.instance.password and old_password:
            if not self.instance.check_password(old_password):
                raise forms.ValidationError("Old password is incorrect")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
