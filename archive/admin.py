from cards.admin import (CodeBatchResource, NFCCardInline,
                         PurchasingCodeInline, URLBatchResource)
from django.contrib import admin, messages
from django.http import HttpResponse
from import_export.formats.base_formats import CSV, XLSX
from io import BytesIO
import zipfile
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
    actions = [unarchive_selected, 'export_selected_records']

    def export_selected_records(self, request, queryset):
        export_format = request.POST.get("file_format", "xlsx")
        resource = self.resource_class()
        resource.context = {"export_format": export_format}

        if export_format == "xlsx":
            file_format = XLSX()
        else:
            file_format = CSV()

        responses = []
        for batch in queryset:
            dataset = resource.export([batch])

            batch_name = str(batch).replace(" ", "_")
            file_name = f"{batch_name}_{batch.pk}.{file_format.get_extension()}"
            export_data = file_format.export_data(dataset)
            response = HttpResponse(
                export_data, content_type=file_format.get_content_type()
            )
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'
            responses.append((file_name, response.content))

        if len(responses) == 1:
            return HttpResponse(
                responses[0][1],
                content_type=file_format.get_content_type(),
                headers={
                    "Content-Disposition": f'attachment; filename="{responses[0][0]}"'
                },
            )
        else:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, content in responses:
                    zip_file.writestr(file_name, content)

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="exported_archived_url_batches.zip"'
            return response

    export_selected_records.short_description = "Export Selected Records"

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
    actions = [unarchive_selected, 'export_selected_records']

    def export_selected_records(self, request, queryset):
        export_format = request.POST.get("file_format", "xlsx")
        resource = self.resource_class()
        resource.context = {"export_format": export_format}

        if export_format == "xlsx":
            file_format = XLSX()
        else:
            file_format = CSV()

        responses = []
        for batch in queryset:
            dataset = resource.export([batch])

            batch_name = str(batch).replace(" ", "_")
            file_name = f"{batch_name}_{batch.pk}.{file_format.get_extension()}"
            export_data = file_format.export_data(dataset)
            response = HttpResponse(
                export_data, content_type=file_format.get_content_type()
            )
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'
            responses.append((file_name, response.content))

        if len(responses) == 1:
            return HttpResponse(
                responses[0][1],
                content_type=file_format.get_content_type(),
                headers={
                    "Content-Disposition": f'attachment; filename="{responses[0][0]}"'
                },
            )
        else:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, content in responses:
                    zip_file.writestr(file_name, content)

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="exported_archived_code_batches.zip"'
            return response

    export_selected_records.short_description = "Export Selected Records"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False
