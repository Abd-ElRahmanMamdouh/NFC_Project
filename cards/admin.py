import uuid
from import_export.formats.base_formats import XLSX, CSV
from core.utils import unique_code_generator, unique_password_generator
from django.contrib import admin, messages
from django.http import HttpResponse
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource
from settings.models import ProductGroup
from import_export.admin import ImportExportModelAdmin
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
        fields = ("group__title", 'poduct', "card__uuid", "duration__duration", "code", "passwod", "created_at", "updated_at")
        model = PurchasingCode


@admin.register(NFCCard)
class NFCCardAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_url", "card_code", "created_at", "updated_at"]
    fields = ["uuid", "user"]
    readonly_fields = ["uuid", "batch"]
    resource_class = NFCCardResource

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create-url-batch/', self.bulk_create_view, name='url_bulk'),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == 'POST':
            form = URLBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data['count']
                user = request.user
                batch = URLBatch.objects.create(count=count, user=user)
                instances = [NFCCard(uuid=uuid.uuid4(), batch=batch) for _ in range(count)]
                NFCCard.objects.bulk_create(instances)

                self.message_user(request, f'Successfully created {count} URLS.', messages.SUCCESS)
                return redirect('admin:cards_urlbatch_changelist')

        else:
            form = URLBulkCreateForm()

        extra_context = {
            'title': 'Create URL Batch',
            'head_title': 'URL Generator',
            'form': form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, 'admin/bulk_create_form.html', context)


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

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create-code-batch/', self.bulk_create_view, name='code_bulk'),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == 'POST':
            form = CodeBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data['count']
                product = form.cleaned_data['product']
                duration = form.cleaned_data['duration']
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
                        instance = PurchasingCode(group=group, duration=duration, batch=batch)
                        instance.generate_code_and_password()
                        instances.append(instance)
                else:
                    instances = []
                    for _ in range(count):
                        instance = PurchasingCode(product=product, duration=duration, batch=batch)
                        instance.generate_code_and_password()
                        instances.append(instance)
                PurchasingCode.objects.bulk_create(instances)
                self.message_user(request, f'Successfully created {count} Purchasing Codes.', messages.SUCCESS)
                return redirect('admin:cards_codebatch_changelist')

        else:
            form = CodeBulkCreateForm()

        extra_context = {
            'title': 'Create Purchasing Code Batch',
            'head_title': 'Code Generator',
            'form': form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, 'admin/bulk_create_form.html', context)


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


class NFCCardResourceInline(ModelResource):
    get_url = Field(column_name='URL', attribute='get_url')

    class Meta:
        fields = ("get_url", )
        model = NFCCard

class URLBatchResource(ModelResource):
    batch_urls = Field()
    user_username = Field(column_name='User', attribute='user__username')

    class Meta:
        fields = ("count", "user_username", "created_at", "batch_urls",)
        model = URLBatch

    def dehydrate_batch_urls(self, batch):
        export_format = self.context.get('export_format')
        inline_queryset = NFCCard.objects.filter(batch=batch)
        inline_resource = NFCCardResourceInline()
        dataset = inline_resource.export(inline_queryset)
        if export_format == 'xlsx':
            return dataset.xlsx
        else:
            return dataset.csv


class CodeResourceInline(ModelResource):
    class Meta:
        fields = ("code", )
        model = PurchasingCode


class CodeBatchResource(ModelResource):
    batch_codes = Field()
    user_username = Field(column_name='User', attribute='user__username')

    class Meta:
        fields = ("count", "user_username", "created_at", "batch_urls",)
        model = CodeBatch

    def dehydrate_batch_codes(self, batch):
        export_format = self.context.get('export_format')
        inline_queryset = PurchasingCode.objects.filter(batch=batch)
        inline_resource = CodeResourceInline()
        dataset = inline_resource.export(inline_queryset)
        if export_format == 'xlsx':
            return dataset.xlsx
        else:
            return dataset.csv


@admin.register(URLBatch)
class URLBatchAdmin(admin.ModelAdmin):
    resource_class = URLBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]
    actions = [archive_selected, 'export_selected_record']

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
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False


@admin.register(CodeBatch)
class CodeBatchAdmin(admin.ModelAdmin):
    resource_class = CodeBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]
    actions = [archive_selected, 'export_selected_record']

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
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False
