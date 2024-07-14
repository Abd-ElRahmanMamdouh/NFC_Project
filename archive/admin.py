from cards.models import CodeBatch, NFCCard, PurchasingCode, URLBatch
from django.contrib import admin
from django.contrib.admin import site
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from .models import URLBatchArchived
from cards.admin import NFCCardInline


@admin.register(URLBatchArchived)
class URLBatchArchivedAdmin(admin.ModelAdmin):
    list_display = ["count", "created_at", "user", "archive"]
    list_editable = ["archive"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False
