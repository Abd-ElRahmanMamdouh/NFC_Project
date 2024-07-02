from django.contrib import admin
from .models import PurchasingCode, NFCCard


@admin.register(PurchasingCode)
class PurchasingCodeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "group", "created_at", "updated_at"]
    filter_horizontal = ("extra_products",)
    readonly_fields = ["code", "password"]


@admin.register(NFCCard)
class NFCCardAdmin(admin.ModelAdmin):
    list_display = ["__str__", "code", "created_at", "updated_at"]
    readonly_fields = ["user"]
