from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ManyToManyWidget
from django.utils.safestring import mark_safe
from .forms import PurchasingCodeForm
from .models import NFCCard, Product, ProductGroup, PurchasingCode

User = get_user_model()


class NFCCardResource(ModelResource):
    class Meta:
        fields = ("uuid", "user__username", "card_code", "created_at", "updated_at")
        model = NFCCard


class ProductResource(ModelResource):
    groups = Field(
        column_name="groups",
        attribute="product_groups",
        widget=ManyToManyWidget(ProductGroup, field="title"),
    )

    class Meta:
        fields = ("title", "price", "groups", "created_at", "updated_at")
        model = Product


class ProductGroupResource(ModelResource):
    products = Field(
        column_name="products",
        attribute="products",
        widget=ManyToManyWidget(Product, field="title"),
    )

    class Meta:
        fields = ("title", "price", "products", "created_at", "updated_at")
        model = ProductGroup


class PurchasingCodeInline(admin.StackedInline):
    model = PurchasingCode
    filter_horizontal = ("extra_products",)
    verbose_name_plural = "Purchasing Code"
    readonly_fields = ["code", "password"]
    can_delete = False
    form = PurchasingCodeForm


@admin.register(NFCCard)
class NFCCardAdmin(ExportMixin, admin.ModelAdmin):
    inlines = [PurchasingCodeInline]
    list_display = ["__str__", "get_url", "card_code", "created_at", "updated_at"]
    fields = ["uuid", "user"]
    readonly_fields = ["user", "uuid"]
    resource_class = NFCCardResource

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["uuid"]
        return self.readonly_fields

    def get_url(self, obj):
        print(obj.get_absolute_url())
        url = obj.get_absolute_url()
        url_button = f'<a href="{ url }">View On Site</a>'
        return mark_safe(url_button)

    get_url.short_description = "URL"


@admin.register(ProductGroup)
class ProductGroupAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "price", "created_at", "updated_at"]
    filter_horizontal = ("products",)
    resource_class = ProductGroupResource


@admin.register(Product)
class ProductAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "price", "created_at", "updated_at"]
    actions = None
    resource_class = ProductResource

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        related_objects = obj.get_related_objects()

        if related_objects.exists():
            message = (
                f"The product '{obj}' is related to the following Groups: "
                f"{', '.join(str(related_obj) for related_obj in related_objects)}. "
                f"Deleting it will also remove it from these groups."
            )
            self.message_user(request, message, level=messages.WARNING)

        return super().delete_view(request, object_id, extra_context=extra_context)
