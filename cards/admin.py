import uuid

from io import BytesIO
import zipfile
from django.contrib import admin, messages
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.formats.base_formats import CSV, XLSX
from import_export.resources import ModelResource
from settings.models import ProductGroup
from tablib import Dataset

from .forms import CodeBulkCreateForm, URLBulkCreateForm
from .models import CodeBatch, NFCCard, PurchasingCode, URLBatch

User = get_user_model()


def archive_selected(modeladmin, request, queryset):
    queryset.update(archive=True)
    messages.success(request, "Selected records have been archived.")


class NFCCardResource(ModelResource):
    class Meta:
        fields = ("uuid", "user__username", "card_code", "created_at", "updated_at")
        model = NFCCard


class PurchasingCodeResource(ModelResource):
    class Meta:
        fields = (
            "group__title",
            "poduct",
            "card__uuid",
            "duration__duration",
            "code",
            "passwod",
            "created_at",
            "updated_at",
        )
        model = PurchasingCode


@admin.register(NFCCard)
class NFCCardAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_url", "card_code", "created_at", "updated_at"]
    fields = ["uuid", "user"]
    readonly_fields = ["uuid", "batch"]
    resource_class = NFCCardResource

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(batch__archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("create-url-batch/", self.bulk_create_view, name="url_bulk"),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == "POST":
            form = URLBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data["count"]
                user = request.user
                batch = URLBatch.objects.create(count=count, user=user)
                instances = [
                    NFCCard(uuid=uuid.uuid4(), batch=batch) for _ in range(count)
                ]
                NFCCard.objects.bulk_create(instances)

                self.message_user(
                    request, f"Successfully created {count} URLS.", messages.SUCCESS
                )
                return redirect("admin:cards_urlbatch_changelist")

        else:
            form = URLBulkCreateForm()

        extra_context = {
            "title": "Create URL Batch",
            "head_title": "URL Generator",
            "form": form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, "admin/bulk_create_form.html", context)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["uuid"]
        return self.readonly_fields

    def get_url(self, obj):
        url = obj.get_absolute_url()
        url_button = f'<a href="{ url }">View On Site</a>'
        return mark_safe(url_button)

    get_url.short_description = "URL"


@admin.register(PurchasingCode)
class PurchasingCodeAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "created_at", "updated_at"]
    fields = ["group", "product", "duration", "card", "code", "password"]
    readonly_fields = ["code", "password", "card"]
    resource_class = PurchasingCodeResource

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(batch__archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("create-code-batch/", self.bulk_create_view, name="code_bulk"),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == "POST":
            form = CodeBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data["count"]
                product = form.cleaned_data["product"]
                duration = form.cleaned_data["duration"]
                try:
                    group = ProductGroup.objects.get(id=product)
                except ProductGroup.DoesNotExist:
                    group = None
                except ValueError:
                    group = None
                user = request.user
                batch = CodeBatch.objects.create(count=count, user=user)
                if group:
                    instances = []
                    for _ in range(count):
                        instance = PurchasingCode(
                            group=group, duration=duration, batch=batch
                        )
                        instance.generate_code_and_password()
                        instances.append(instance)
                else:
                    instances = []
                    for _ in range(count):
                        instance = PurchasingCode(
                            product=product, duration=duration, batch=batch
                        )
                        instance.generate_code_and_password()
                        instances.append(instance)
                PurchasingCode.objects.bulk_create(instances)
                self.message_user(
                    request,
                    f"Successfully created {count} Purchasing Codes.",
                    messages.SUCCESS,
                )
                return redirect("admin:cards_codebatch_changelist")

        else:
            form = CodeBulkCreateForm()

        extra_context = {
            "title": "Create Purchasing Code Batch",
            "head_title": "Code Generator",
            "form": form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, "admin/bulk_create_form.html", context)


class NFCCardInline(admin.TabularInline):
    model = NFCCard
    fields = ["get_url"]
    readonly_fields = ["get_url"]
    can_delete = False
    extra = 0
    show_change_link = True

    def get_url(self, instance):
        base_url = "http://127.0.0.1:8000/services/landingPage/"
        url = f"{ base_url }{instance.uuid}/"
        return url

    get_url.short_description = "URL"


class PurchasingCodeInline(admin.TabularInline):
    model = PurchasingCode
    fields = ["card", "password", "code"]
    readonly_fields = ["card", "password", "code"]
    can_delete = False
    extra = 0
    show_change_link = True


class URLBatchResource(ModelResource):
    batch_url = Field(column_name="URL")
    batch_str = Field(column_name="Batch")

    class Meta:
        fields = ("batch_str", "batch_url")
        model = URLBatch

    def dehydrate_batch_url(self, batch):
        return None

    def dehydrate_batch_str(self, batch):
        return str(batch)

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for batch in queryset:
            inline_queryset = NFCCard.objects.filter(batch=batch)
            for card in inline_queryset:
                try:
                    card_code = card.card_code
                except PurchasingCode.DoesNotExist:
                    card_code = "No Code connected yet"
                last_updated = card.updated_at.strftime("%Y-%m-%d, %H:%M %p")
                data.append(
                    {
                        "Batch": str(batch),
                        "Card User": card.user.username
                        if card.user
                        else "No User connected yet",
                        "Card UUID": card.uuid,
                        "Card Code": card_code,
                        "Last Updated": last_updated,
                        "URL": card.get_url(),
                    }
                )

        headers = [
            "Batch",
            "Card User",
            "Card UUID",
            "Card Code",
            "Last Updated",
            "URL",
        ]
        dataset = self._create_dataset(data, headers)

        return dataset

    def _create_dataset(self, data, headers):
        dataset = Dataset()
        dataset.headers = headers
        for row in data:
            dataset.append([row[col] for col in headers])

        return dataset


class CodeBatchResource(ModelResource):
    code = Field(column_name="Code")
    batch_str = Field(column_name="Batch")

    class Meta:
        fields = (
            "batch_str",
            "code",
        )
        model = CodeBatch

    def dehydrate_code(self, batch):
        return None

    def dehydrate_batch_str(self, batch):
        return str(batch)

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []

        for batch in queryset:
            inline_queryset = PurchasingCode.objects.filter(batch=batch)
            for code in inline_queryset:
                if code.group:
                    product = code.group
                else:
                    product = code.get_product_display()
                last_updated = code.updated_at.strftime("%Y-%m-%d, %H:%M %p")
                data.append(
                    {
                        "Batch": str(batch),
                        "Code": code.code,
                        "Password": code.password,
                        "Duration": code.duration,
                        "Product": product,
                        "Card": code.card if code.card else "No Card connected yet",
                        "Last Updated": last_updated,
                    }
                )

        headers = [
            "Batch",
            "Code",
            "Password",
            "Duration",
            "Product",
            "Card",
            "Last Updated",
        ]
        dataset = self._create_dataset(data, headers)

        return dataset

    def _create_dataset(self, data, headers):
        dataset = Dataset()
        dataset.headers = headers
        for row in data:
            dataset.append([row[col] for col in headers])

        return dataset


@admin.register(URLBatch)
class URLBatchAdmin(admin.ModelAdmin):
    resource_class = URLBatchResource
    list_display = ["__str__", "count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]
    actions = [archive_selected, "export_selected_records"]

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
            ] = 'attachment; filename="exported_url_batches.zip"'
            return response

    export_selected_records.short_description = "Export Selected Records"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False


@admin.register(CodeBatch)
class CodeBatchAdmin(admin.ModelAdmin):
    resource_class = CodeBatchResource
    list_display = ["__str__", "count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]
    actions = [archive_selected, "export_selected_records"]

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
            ] = 'attachment; filename="exported_code_batches.zip"'
            return response

    export_selected_records.short_description = "Export Selected Records"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False
