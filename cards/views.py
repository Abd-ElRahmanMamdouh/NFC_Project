from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import UpdateView
from hitcount.views import HitCountDetailView
from django.contrib.auth.decorators import login_required
from .forms import NFCCardForm
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
    form_class = NFCCardForm

    def get_queryset(self):
        user = self.request.user
        qs = self.model.objects.filter(user=user)
        return qs
