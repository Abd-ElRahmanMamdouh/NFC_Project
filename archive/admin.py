from cards.models import NFCCard, PurchasingCode
from django.contrib import admin

from .models import CodeBatch, URLBatch


class NFCCardInline(admin.TabularInline):
    model = NFCCard
    fields = ["get_url"]
    readonly_fields = ["get_url"]
    can_delete = False
    extra = 0
    show_change_link = True
    

    def get_url(self, instance):
        base_url = 'http://127.0.0.1:8000/services/landingPage/'
        url = f'{ base_url }{instance.uuid}/'
        return url

    get_url.short_description = "URL"


class PurchasingCodeInline(admin.TabularInline):
    model = PurchasingCode
    fields = ["card", "password", "code"]
    readonly_fields = ["card", "password", "code"]
    can_delete = False
    extra = 0
    show_change_link = True


@admin.register(URLBatch)
class URLBatchAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]

    def has_add_permission(self, request):
        return False


@admin.register(CodeBatch)
class CodeBatchAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]

    def has_add_permission(self, request):
        return False
