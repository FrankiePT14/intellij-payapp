from django import forms
from . import models
from .models import CurrencyTransfer
from .models import CurrencyRequest


class CurrencyTransferForm(forms.ModelForm):
    class Meta:
        model = CurrencyTransfer
        fields = ["enter_your_destination_username", "enter_amount_to_transfer"]


class CurrencyRequestForm(forms.ModelForm):
    class Meta:
        model = CurrencyRequest
        fields = ["enter_the_username_you_want_to_request_from", "enter_amount_to_request"]
