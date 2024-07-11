import uuid

from archive.models import CodeBatch, URLBatch
from django.contrib import admin, messages
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin
from import_export.resources import ModelResource
from settings.models import ProductGroup
from core.utils import unique_code_generator, unique_password_generator
from .forms import CodeBulkCreateForm, URLBulkCreateForm
from .models import NFCCard, PurchasingCode

User = get_user_model()


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
                return redirect('admin:archive_urlbatch_changelist')

        else:
            form = URLBulkCreateForm()

        extra_context = {
            'title': 'Create URL Batch',
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
                return redirect('admin:archive_codebatch_changelist')

        else:
            form = CodeBulkCreateForm()

        extra_context = {
            'title': 'Create Purchasing Code Batch',
            'form': form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, 'admin/bulk_create_form.html', context)
