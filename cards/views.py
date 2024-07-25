from core.utils import handle_uploaded_file
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import ListView, UpdateView
from hitcount.views import HitCountDetailView

from .forms import (BusinessCardForm, GalleryForm, LetterForm, NFCCardForm,
                    PDFViewerFom, ProductViewerForm, RedirectUrlForm,
                    VideoMessageForm)
from .models import NFCCard, PurchasingCode


class NFCCardView(HitCountDetailView):
    template_name = "cards/langing_page_detail.html"
    model = NFCCard
    context_object_name = "card"
    count_hit = True

    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uidb64")
        return get_object_or_404(self.model, uuid=uuid)


def link_new_card(request, uidb64):
    if request.method == "POST":
        code = request.POST.get('code')
        try:
            code = PurchasingCode.objects.get(code=code, card__isnull=True)
        except PurchasingCode.DoesNotExist:
            msg = "Wrong Code or used before"
            messages.error(request, msg)
            return redirect("cards:link_new_card", uidb64=uidb64)
        card = get_object_or_404(NFCCard, uuid=uidb64)
        card.user = request.user
        card.save()
        code.card = card
        code.save()
        msg = "Card Linked Successfully"
        messages.success(request, msg)
        return redirect("home")
    return render(request, 'cards/card_register.html', {})


def check_password(request, uidb64):
    if request.method == "POST":
        card = get_object_or_404(NFCCard, uuid=uidb64)
        password = request.POST.get('password')
        if card.password == password:
            request.session['password_correct'] = True
            return redirect(card.get_absolute_url())
        else:
            request.session['password_correct'] = False
            msg = "Wrong Password, Try Again"
            messages.error(request, msg)
            return redirect(card.get_absolute_url())
    else:
        return redirect(card.get_absolute_url())


class NFCCardUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = NFCCard
    template_name = 'base/forms/create_update.html'
    success_message = "Password successfully updated"
    success_url = reverse_lazy("cards:user_dashboard")
    form_class = NFCCardForm

    def get_queryset(self):
        user = self.request.user
        qs = self.model.objects.filter(user=user)
        return qs


class NFCCardListView(LoginRequiredMixin, ListView):
    model = NFCCard
    template_name = 'user/dashboard.html'


def update_business_card(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = BusinessCardForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            show = form.cleaned_data.get('show')
            logo = request.FILES.get('logo')

            existing_data = card.data or {}
            existing_logo_url = existing_data.get('business_card', {}).get('logo_url', '')
            logo_url = handle_uploaded_file(request, logo) if logo else existing_logo_url
            json_data = {
                'title': title,
                'desc': desc,
                'logo_url': logo_url,
                'show': show
            }
            data = existing_data
            data['business_card'] = json_data
            if show:
                data['choosen_product'] = {'product': 'business_card'}
                data['redirect_url']['show'] = not show
                data['gallery']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:user_dashboard")
        else:
            msg = mark_safe(form.errors)
            messages.error(request, msg)
            return redirect("cards:user_dashboard")
    else:
        if card.data:
            initial_data = card.data.get('business_card', {})
            logo_url = initial_data.get('logo_url', '')
        else:
            initial_data = {}
            logo_url = None
        form = BusinessCardForm(initial=initial_data)
    
    return render(request, 'cards/forms/business_card.html', {'form': form, 'logo_url': logo_url})


def update_gallery(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        gallery_data = None
        if form.is_valid():
            files = request.FILES.getlist('images')
            show = form.cleaned_data.get('show')
            image_urls = []
            for file in files:
                file_url = handle_uploaded_file(request, file)
                image_urls.append(file_url)
            
            data = card.data or {}
            data['gallery'] = {'images': image_urls, 'show': show}
            if show:
                data['choosen_product'] = {'product': 'gallery'}
                data['business_card']['show'] = not show
                data['redirect_url']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:user_dashboard")
        else:
            msg = mark_safe(form.errors)
            messages.error(request, msg)
            return redirect("cards:user_dashboard")
    else:
        initial_data = card.data.get('gallery', {})
        gallery_data = card.data.get('gallery', {}).get('images', [])
        form = GalleryForm(initial=initial_data)

    return render(request, 'cards/forms/gallery.html', {'form': form, 'gallery_data': gallery_data})


def update_redirect_url(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = RedirectUrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url')
            show = form.cleaned_data.get('show')
            existing_data = card.data or {}
            json_data = {
                'url': url,
                'show': show
            }
            data = existing_data
            data['redirect_url'] = json_data
            if show:
                data['choosen_product'] = {'product': 'redirect_url'}
                data['business_card']['show'] = not show
                data['gallery']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:user_dashboard")
        else:
            msg = mark_safe(form.errors)
            messages.error(request, msg)
            return redirect("cards:user_dashboard")
    else:
        if card.data:
            initial_data = card.data.get("redirect_url", {})
        else:
            initial_data = {}
        form = RedirectUrlForm(initial=initial_data)
    
    return render(request, 'cards/forms/redirect_url.html', {'form': form})

def update_video_message(request, uidb64):
    text = "This Page is under development"
    return render(request, 'cards/forms/test.html', {'text': text})


def update_product_viewer(request, uidb64):
    text = "This Page is under development"
    return render(request, 'cards/forms/test.html', {'text': text})


def update_pdf_viewer(request, uidb64):
    text = "This Page is under development"
    return render(request, 'cards/forms/test.html', {'text': text})


def update_letter(request, uidb64):
    text = "This Page is under development"
    return render(request, 'cards/forms/test.html', {'text': text})
