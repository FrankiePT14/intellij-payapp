
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from payapp.models import Currency


class SignUpForm(UserCreationForm):
    currency_type = forms.ChoiceField(choices=Currency.CURRENCY_CHOICES, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "currency_type")

        def save(self, *args, **kwargs):
            instance = super(SignUpForm, self).save(*args, **kwargs)
            Currency.objects.create(name=instance, currency=self.cleaned_data['currency'])
            return instance

