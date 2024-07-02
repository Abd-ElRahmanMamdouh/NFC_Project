from django.contrib import admin, messages

from .models import Product, ProductGroup


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ["__str__", "price", "created_at", "updated_at"]
    filter_horizontal = ("products",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["__str__", "price", "created_at", "updated_at"]
    actions = None

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
