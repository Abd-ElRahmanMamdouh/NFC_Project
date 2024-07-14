from cards.models import CodeBatch, NFCCard, PurchasingCode, URLBatch
from django.contrib import admin, messages
from django.contrib.admin import site
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from .models import URLBatchArchived, CodeBatchArchived
from cards.admin import NFCCardInline, PurchasingCodeInline


def unarchive_selected(modeladmin, request, queryset):
    queryset.update(archive=False)
    messages.success(request, "Selected records have been un archived.")


@admin.register(URLBatchArchived)
class URLBatchArchivedAdmin(admin.ModelAdmin):
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]
    actions = [unarchive_selected]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False

@admin.register(CodeBatchArchived)
class CodeBatchArchivedAdmin(admin.ModelAdmin):
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]
    actions = [unarchive_selected]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False
