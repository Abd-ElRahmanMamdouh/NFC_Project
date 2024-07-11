from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource

from .forms import ProductGroupForm
from .models import ProductGroup, LinkDuration


class ProductGroupResource(ModelResource):
    products = Field(
        column_name="products",
        attribute="products",
    )

    class Meta:
        fields = ("title", "price", "products", "created_at", "updated_at")
        model = ProductGroup


@admin.register(ProductGroup)
class ProductGroupAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "price", "get_products_display", "created_at", "updated_at"]
    resource_class = ProductGroupResource
    form = ProductGroupForm

    def get_products_display(self, obj):
        return obj.get_products_display()

    get_products_display.short_description = "Products"


@admin.register(LinkDuration)
class LinkDurationAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
