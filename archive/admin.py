from cards.admin import (CodeBatchResource, CodeResourceInline, NFCCardInline,
                         NFCCardResourceInline, PurchasingCodeInline,
                         URLBatchResource)
from cards.models import CodeBatch, NFCCard, PurchasingCode, URLBatch
from django.contrib import admin, messages
from django.contrib.admin import site
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from import_export.formats.base_formats import CSV, XLSX

from .models import CodeBatchArchived, URLBatchArchived


def unarchive_selected(modeladmin, request, queryset):
    queryset.update(archive=False)
    messages.success(request, "Selected records have been un archived.")



@admin.register(URLBatchArchived)
class URLBatchArchivedAdmin(admin.ModelAdmin):
    resource_class = URLBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]
    actions = [unarchive_selected, 'export_selected_record']

    def export_selected_record(self, request, queryset):

        record = queryset.first()
        export_format = request.POST.get('file_format', 'csv')
        resource = self.resource_class()
        resource.context = {'export_format': export_format}

        dataset = resource.export([record])

        # Determine the export format
        if export_format == 'xlsx':
            file_format = XLSX()
        else:
            file_format = CSV()

        export_data = file_format.export_data(dataset)
        response = HttpResponse(export_data, content_type=file_format.get_content_type())
        response['Content-Disposition'] = f'attachment; filename="{record}.xlsx"'

        return response

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False


@admin.register(CodeBatchArchived)
class CodeBatchArchivedAdmin(admin.ModelAdmin):
    resource_class = CodeBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]
    actions = [unarchive_selected, 'export_selected_record']

    def export_selected_record(self, request, queryset):

        record = queryset.first()
        export_format = request.POST.get('file_format', 'csv')
        resource = self.resource_class()
        resource.context = {'export_format': export_format}

        dataset = resource.export([record])

        # Determine the export format
        if export_format == 'xlsx':
            file_format = XLSX()
        else:
            file_format = CSV()

        export_data = file_format.export_data(dataset)
        response = HttpResponse(export_data, content_type=file_format.get_content_type())
        response['Content-Disposition'] = f'attachment; filename="{record}.xlsx"'

        return response

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False
