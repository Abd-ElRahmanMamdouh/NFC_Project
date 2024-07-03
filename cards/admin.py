from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ManyToManyWidget

from .forms import CodeForm
from .models import NFCCard, Product, ProductGroup, PurchasingCode

User = get_user_model()


class NFCCardResource(ModelResource):
    class Meta:
        fields = ('uuid', 'user__username', 'card_code', 'created_at', 'updated_at')
        model = NFCCard


class ProductResource(ModelResource):
    groups = Field(
        column_name='groups',
        attribute='product_groups',
        widget=ManyToManyWidget(ProductGroup, field='title')        
    )
    class Meta:
        fields = ('title', 'price', 'groups', 'created_at', 'updated_at')
        model = Product


class ProductGroupResource(ModelResource):
    products = Field(
        column_name='products',
        attribute='products',
        widget=ManyToManyWidget(Product, field='title')        
    )
    class Meta:
        fields = ('title', 'price', 'products', 'created_at', 'updated_at')
        model = ProductGroup


class PurchasingCodeInline(admin.StackedInline):
    model = PurchasingCode
    filter_horizontal = ("extra_products",)
    verbose_name_plural = 'Purchasing Code'
    readonly_fields = ['code', 'password']
    form = CodeForm    


@admin.register(NFCCard)
class NFCCardAdmin(ExportMixin, admin.ModelAdmin):
    inlines = [PurchasingCodeInline]
    list_display = ["__str__", "card_code", "created_at", "updated_at"]
    fields = ['uuid', 'user']
    readonly_fields = ["user", "uuid"]
    resource_class = NFCCardResource


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
        related_objects = (
            obj.get_related_objects()
        )  # Replace with your method to fetch related objects

        if related_objects.exists():
            message = (
                f"The product '{obj}' is related to the following Groups: "
                f"{', '.join(str(related_obj) for related_obj in related_objects)}. "
                f"Deleting it will also remove it from these groups."
            )
            self.message_user(request, message, level=messages.WARNING)

        return super().delete_view(request, object_id, extra_context=extra_context)
